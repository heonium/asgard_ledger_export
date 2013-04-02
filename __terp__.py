{
	"name":"Asgard : Ledger plugin",
	"license":"CeCILL",
	"version":"0.01",
	"author":"Heonium",
	"website":"http://www.heonium.com",
	"category":"Heonium/Asgard",
	"description":
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
	"depends":['base', 'account', 'document', 'hnm_common'],
	"init_xml":[
	],
	"update_xml":[
        'data/asgard_ledger_export_data.xml',
        'asgard_ledger_export_view.xml',
    ],
	"active": False,
	"installable": True,
}
