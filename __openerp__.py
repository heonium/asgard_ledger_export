# -*- coding: utf-8 -*-
###############################################################################
#
# Asgard Ledger Export (ALE) module,
# Copyright (C) 2005 - 2013
# Héonium (http://www.heonium.com). All Right Reserved
#
# Asgard Ledger Export (ALE) module
# is free software: you can redistribute it and/or modify it under the terms
# of the Affero GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Asgard Ledger Export (ALE) module
# is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Affero GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


{
    'name': "Héonium: Asgard Ledger Export (ALE)",
    'summary': "Asgard Ledger Export (ALE)",
    'license': "AGPL-3",
    'version': "1.0",
    'author': "Heonium",
    'website': "http://www.heonium.com",
    'category': "Héonium/Client",
    "sequence": 50,
    'description':
    """
Description
============

Plugin used to export ledger entries to external Ledger software.
You can define which fields you want export.

Use
============
After configurating this module, you can add a statement to select
which entry you want to export. After that you can export the selected
entry.

It create a attached file to this statement. Now you can
see or download the attached file and import it in your other ledger
software.
See doc/asgard_ledger_export_fr.pdf for more details

    """,
    'depends': [
        'base',
        'account',
        'document',
        'heo_common'
    ],
    'init_xml': [],
    'demo': [],
    'data': [
        'security/asgard_ledger_export_security.xml',
        'security/ir.model.access.csv',
        'data/asgard_ledger_export_data.xml',
        'asgard_ledger_export_view.xml',
    ],
    'active': False,
    'installable': True,
    'application': True,
}
