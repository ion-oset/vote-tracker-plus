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

"""generate_all_blank_ballots.py - generate all possible blank ballots

See 'generate_all_blank_ballots.py -h' for usage information.
"""

# Standard imports
import sys

# Local import
from vtp.ops.generate_all_blank_ballots_operation import (
    GenerateAllBlankBallotsOperation,
)


################
# main
################
def main():
    """
    Called via a python local install entrypoint or by running this
    file.  Simply wraps the scripts constructor and calls the run
    method.  See the script's help output or read the
    vtp.ops.generate_all_blank_ballots_operation.py (argparse)
    description in the source file.
    """

    # do it
    gabbo = GenerateAllBlankBallotsOperation(sys.argv[1:])
    gabbo.run()


# If called directly via this file
if __name__ == "__main__":
    main()

# EOF