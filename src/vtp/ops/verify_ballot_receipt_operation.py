#!/usr/bin/env python

#  VoteTrackerPlus
#   Copyright (C) 2022 Sandy Currier
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Logic of operation for verifying receipt of a ballot."""

# Standard imports
import json
import logging
import re

# Project imports
from vtp.core.ballot import Ballot
from vtp.core.common import Common, Shellout
from vtp.core.election_config import ElectionConfig

# Local imports
from .operation import Operation


class VerifyBallotReceiptOperation(Operation):
    """
    A class to implememt the verify-ballot-receipt operation.  See the
    verify-ballot-receipt help output or read the parse_argument argparse
    description (immediately below this) in the source file.
    """

    def __init__(
        self,
        election_data_dir: str = "",
        guid: str = "",
        verbosity: int = 3,
        printonly: bool = False,
    ):
        """
        Primarily to module-ize the scripts and keep things simple,
        idiomatic, and in different namespaces.
        """
        super().__init__(election_data_dir, verbosity, printonly, guid)

    # pylint: disable=too-many-arguments   # self is not technically an arg kind-of
    def validate_ballot_lines(
        self, lines, headers, uids, the_election_config, error_digests
    ):
        """Will scan the supplied ballot lines for invalid digests.  Will
        print and return the invalid digests.
        """
        input_data = ""
        for line in lines:
            input_data += "\n".join(line) + "\n"
        with Shellout.changed_cwd(the_election_config.get("git_rootdir")):
            results = (
                Shellout.run(
                    [
                        "git",
                        "cat-file",
                        "--buffer",
                        "--batch-check=%(objectname) %(objecttype)",
                    ],
                    input=input_data,
                    text=True,
                    check=True,
                    verbosity=self.verbosity,
                    capture_output=True,
                )
                .stdout.strip()
                .splitlines()
            )
        # Print any invalid digest info
        row_length = len(uids)
        # Mmm - 1 based?
        row = 1
        column = 1
        for line in results:
            digest, commit_type = line.split()
            if commit_type == "missing":
                logging.error(
                    "[ERROR]: missing digest: row %s column %s contest=%s digest=%s",
                    row,
                    column,
                    headers[column - 1],
                    digest,
                )
                error_digests.add(digest)
            elif commit_type != "commit":
                logging.error(
                    "[ERROR]: invalid digest type: row %s column %s contest=%s digest=%s type=%s",
                    row,
                    column,
                    headers[column - 1],
                    digest,
                    commit_type,
                )
                error_digests.add(digest)
            column += 1
            if column > row_length:
                column = 1
                row += 1

    # pylint: disable=too-many-arguments   # self is not technically an arg kind-of
    def vet_rows(
        self,
        lines,
        headers,
        uids,
        the_election_config,
        error_digests,
        row_index=None,
    ):
        """
        Will scan the main branch and validate that the receipt digests
        are there and that they are in the correct contest.
        """
        requested_row = None
        requested_digests = None
        for index, row in enumerate(lines):
            # Note - cannot handle bad digests so they need to be removed
            # prior to the call.  However, the headers and uids are both
            # lists that are assumed to be a complete list, so removing a
            # bad digest(s) becomes complicated.
            legit_row = [dig for dig in row if dig not in error_digests]
            if len(legit_row) == len(row):
                # all the digests are legit
                cvrs = Shellout.cvr_parse_git_log_output(
                    ["git", "log", "--no-walk", "--pretty=format:%H%B"] + row,
                    the_election_config,
                    grouped_by_uid=False,
                    verbosity=self.verbosity - 1,
                )
            elif len(legit_row) > 0:
                # Only some are legitimate
                cvrs = Shellout.cvr_parse_git_log_output(
                    ["git", "log", "--no-walk", "--pretty=format:%H%B"] + legit_row,
                    the_election_config,
                    grouped_by_uid=False,
                    verbosity=self.verbosity - 1,
                )
            else:
                # skip the row - it has no legitimate digests
                continue
            #            import pdb; pdb.set_trace()
            if row_index != "" and int(row_index) - 1 == index:
                requested_row = cvrs
                requested_digests = row
            column = -1
            for digest in row:
                column += 1
                if digest not in legit_row:
                    # skip this digest as it is already non-compliant but
                    # keep incrementing column regardless
                    continue
                if digest not in cvrs:
                    logging.error(
                        "[ERROR]: missing digest in main branch: row %s contest=%s digest=%s",
                        index,
                        headers[column],
                        digest,
                    )
                    error_digests.add(digest)
                    continue
                if cvrs[digest]["CVR"]["uid"] != uids[column]:
                    logging.error(
                        "[ERROR]: bad contest uid: row %s column %s contest %s != %s digest=%s",
                        row,
                        column,
                        headers[column],
                        cvrs[digest]["CVR"]["uid"],
                        digest,
                    )
                    error_digests.add(digest)
                    continue
        return (requested_row, requested_digests)

    # pylint: disable=too-many-locals
    def verify_ballot_receipt(
        self,
        receipt_file,
        the_election_config,
        row_index,
        show_cvr,
    ):
        """Will verify all the rows in a ballot receipt"""

        # Need to get the heeder info as well as the specified row to
        # display.  However, to check the digests that needs/wants to be a
        # different call.

        # At the moment, the validation of the ballot receipt is multiple
        # steps: 1) does the digest exist; 2) is it the correct uid?; 3)
        # is the digest in the tally (legally in main). Some future meta
        # tests could be: 4) does the receipt have a repeated digest?; 5)
        # does it have a valid election uid beyond a valid digest and
        # contest uid (TBD - not implemented yet)

        #    import pdb; pdb.set_trace()
        # Create a ballot to read the receipt file
        a_ballot = Ballot()
        lines = a_ballot.read_receipt_csv(
            the_election_config, receipt_file=receipt_file
        )
        headers = lines.pop(0)
        uids = [re.match(r"([0-9]+)", column).group(0) for column in headers]
        error_digests = set()

        # Now scan all lines (minus the header) for valid digests
        self.validate_ballot_lines(
            lines=lines,
            headers=headers,
            uids=uids,
            the_election_config=the_election_config,
            error_digests=error_digests,
        )

        # Next, make sure the digest are in the correct branch and have a
        # valid CVR content w.r.t. the uid, etc.
        requested_row, requested_digests = self.vet_rows(
            lines=lines,
            headers=headers,
            uids=uids,
            the_election_config=the_election_config,
            error_digests=error_digests,
            row_index=row_index,
        )

        def vet_a_row():
            """
            Will print the actual vote offset in the vote count for each
            contest.  However, to do that need to get the actual complete
            tally for the contests of interest.  And at the moment might
            as well do that for all contests (unless one cat create the
            git grep query syntax to just pull the uids of interest).
            """
            contest_batches = Shellout.cvr_parse_git_log_output(
                ["git", "log", "--topo-order", "--no-merges", "--pretty=format:%H%B"],
                the_election_config,
                verbosity=self.verbosity - 1,
            )
            unmerged_uids = {}
            for u_count, uid in enumerate(uids):
                # For this contest loop over the reverse ordered CVRs (since it
                # seems TBD that it makes sense to ballot #1 as the first ballot on
                # main).
                contest_votes = len(contest_batches[uid])
                found = False
                for c_count, contest in enumerate(contest_batches[uid]):
                    if contest["digest"] in requested_row:
                        print(
                            f"Contest '{contest['CVR']['uid']} - {contest['CVR']['name']}' "
                            f"({contest['digest']}) is vote {contest_votes - c_count} out "
                            f"of {contest_votes} votes"
                        )
                        found = True
                        break
                if found is False:
                    unmerged_uids[uid] = u_count
            if unmerged_uids:
                print("The following contests are not merged to main yet:")
                for uid, offset in unmerged_uids.items():
                    print(f"{headers[offset]} ({requested_digests[offset]})")

        # If a row is specified, will print the context index in the
        # actual contest tally - which basically tells the voter 'your
        # contest is in the tally at index N'
        if row_index:
            valid_digests = []
            for digest in lines[int(row_index) - 1]:
                if digest in error_digests:
                    logging.error(
                        "[ERROR]: cannot print CVR for %s (row %s) - it is invalid",
                        digest,
                        row_index,
                    )
                    continue
                valid_digests.append(digest)
                logging.debug(
                    "%s", json.dumps(requested_row[digest], indent=5, sort_keys=True)
                )
            if show_cvr:
                # Show the CVRs of the row
                with Shellout.changed_cwd(the_election_config.get("git_rootdir")):
                    Shellout.run(["git", "show", "-s"] + valid_digests, check=True)
            else:
                # Just show the summary validation of the row
                vet_a_row()

        # Summerize
        if error_digests:
            logging.error(
                "############\n"
                "[ERROR]: ballot receipt INVALID - the supplied ballot receipt has "
                "%s errors.\n############",
                len(error_digests),
            )
        else:
            print(
                "############\n"
                "[GOOD]: ballot receipt VALID - no digest errors found\n############"
            )

    # pylint: disable=duplicate-code
    def run(
        self,
        receipt_file: str = "",
        row: str = "",
        cvr: bool = False,
    ):
        """Main function - see -h for more info"""

        # Configure logging
        Common.configure_logging(self.verbosity)

        # Create a VTP ElectionData object if one does not already exist
        the_election_config = ElectionConfig.configure_election(self.election_data_dir)

        # git pull the ElectionData repo so to get the latest set of
        # remote CVRs branches
        a_ballot = Ballot()
        with Shellout.changed_cwd(a_ballot.get_cvr_parent_dir(the_election_config)):
            Shellout.run(["git", "pull"], verbosity=self.verbosity, check=True)

        #    import pdb; pdb.set_trace()
        # Can read the receipt file directly without any Ballot info
        self.verify_ballot_receipt(
            receipt_file=receipt_file,
            the_election_config=the_election_config,
            row_index=row,
            show_cvr=cvr,
        )


# EOF
