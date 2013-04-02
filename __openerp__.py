# -*- coding: utf-8 -*-
################################################################################
#
# Héonium Asgard Ledger Export (ALE) module,
# Copyright (C) 2005 - 2012 Héonium (http://heonium.com). All Right Reserved
#
# Héonium Asgard Ledger Export (ALE) module 
# is free software: you can redistribute it and/or modify it under the terms
# of the Affero GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Héonium Asgard Ledger Export (ALE) module
# is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Affero GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
{
    'name': "Asgard : Ledger plugin",
    'license': "AGPL-3",
    'version': "0.09",
    'author': "Heonium",
    'website': "http://www.heonium.com",
    'category': "Heonium/Asgard",
    'description':
"""
Plugin used to export ledger entries to external Ledger software.
You can define which fields you want export.
    - ....
After configurating this module, you can add a statement to select
which entry you want to export. After that you can export the selected
entry. It create a attached file to tis statement. Now you can
see or download the attached file and import it in your other ledger
software
See 'doc/using_asgard_ledger_export_en.pdf' for more details
[TODO]
When you have exported an entry, you must not change this entry. Now
it is possible and we think about to block this possibility.
Perhaps by had à state 'exported' in 'account.move.line' object
""",
    'depends': [
        'base',
        'account',
        'document',
        'hnm_common'
    ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
        'security/asgard_ledger_export_security.xml',
        'security/ir.model.access.csv',
        'data/asgard_ledger_export_data.xml',
        'asgard_ledger_export_view.xml',
    ],
    'active': False,
    'installable': True,
    'images': [],
}
