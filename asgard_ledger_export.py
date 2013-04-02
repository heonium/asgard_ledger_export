# -*- coding: utf-8 -*-
################################################################################
#
#   Asgard Ledger Export (ALE) module,
#   Copyright (C) 2005 - 2012 Héonium (http://heonium.com).
#   All Right Reserved
#
#   Asgard Ledger Export (ALE) module is free software: you can redistribute it
#   and/or modify it under the terms of the Affero GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
#
#   Asgard Ledger Export (ALE) module is distributed in the hope that it will
#   be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   Affero GNU General Public License for more details.
#
#   You should have received a copy of the Affero GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import os
import base64
import copy
import time
import pooler
from osv import fields, osv
from tools.translate import _
from hnm_common.hnm_lib import *
from hnm_common.files_tools import *

##########
### asgard_ledger_export

END_LINE = [('unix', 'Unix','\n'), ('windows','Windows','\r\n'),('nothing','Nothing','')]

class asgard_ledger_export(osv.osv):
    """
    Configuration of export
    """
    _name = "asgard.ledger.export"
    _description = "Define export"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True),
        'separator': fields.char('Separator', size=8, help="Separator field, leave blank if you dont have"),
        'end_line': fields.selection([('unix', 'Unix'), ('windows','Windows'),('nothing','Nothing')],'End of line'),
        'file_header': fields.text('File header', help="Text used to begin file."),
        'extension': fields.char('Extension', size=5, help="String add on end of name file (without the dot).", required=True),
        'alej_line': fields.one2many('asgard.ledger.export.journal', 'asgard_ledger_id', 'Asgard Ledger Journal Lines'),
        'alef_line': fields.one2many('asgard.ledger.export.fields', 'asgard_ledger_id', 'Asgard Ledger Field Lines'),
        'encoding': fields.selection([('utf-8', 'UTF-8'), ('iso-8859-15','ISO-8859-15')], 'Encoding', help="Encoding of exported file"),
        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'active': lambda *a: True,
        'end_line': lambda *a: 'unix',
        'extension': lambda *a: 'csv',
        'file_header': lambda *a: '',
        'separator': lambda *a: ';',
        'encoding': lambda *a: 'utf-8',
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }

    def get_end_line(self, cr, uid, name, context={}):
        result = '\n'
        
        for endline in END_LINE:
            if endline[0] == name: return endline[2]
        
        return result

    def get_building_line(self, cr, uid, ids, context={}):
        """
        Get the table for building line
        """
        pool = pooler.get_pool(cr.dbname)
        alef_obj = pool.get('asgard.ledger.export.fields')
        result = []
        for config in self.browse(cr, uid, ids, context):
            result = alef_obj.get_building_field(cr, uid, map(lambda x:x.id,config.alef_line))
        return result

asgard_ledger_export()

##########
### asgard_ledger_export_journal
class asgard_ledger_export_journal(osv.osv):
    """
    Table d'association entre les journaux comptable d'OpenERP et les noms des
    journaux.
    """
    _name = "asgard.ledger.export.journal"
    _description = "Link beetween OpenERP's journal and Sage journal"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True),
        'asgard_ledger_id': fields.many2one('asgard.ledger.export', 'Asgard Ledger Ref', required=True, ondelete="cascade", select=True,
            help="Associated configuration"),
        'active': fields.boolean('Active'),
        # Association journaux
        'journal_name': fields.char('Journal name', size=10, required=True,
            help="Journal name in target software. Warning, you must put exact name"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, ondelete="cascade",
            help="Select the associated OpenERP's journal"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'active': lambda *a: True,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    _sql_constraints = [
        ('oerp_journal_uniq', 'unique (asgard_ledger_id,journal_id)', _('There is already an association with this journal !')),
    ]
asgard_ledger_export_journal()

class asgard_ledger_export_fields(osv.osv):
    """
    """
    _name = "asgard.ledger.export.fields"
    _description = "Definition of fields"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True, help="Name of this definition"),
        'asgard_ledger_id': fields.many2one('asgard.ledger.export', 'Asgard Ledger Ref', required=True, ondelete="cascade", select=True,
            help="Asgard associated configuration"),
        'sequence': fields.integer('Sequence',help="Order of field (in file target)."),
        'type_field': fields.selection([
            ('account_field','Account field'),
            ('text_field','Text field'),
            ('internal_field','Internal field'),
            ('build_field','Build field')], 'Field type',
                help="Select the type of field\n \
                    Account field : Field of object 'Account'.\n \
                    Internal field : Select field from list.\n \
                    Text field : Only text.\n \
                    Build field : Python code for build value. You can use 'object' and 'time'."),

        'field_account': fields.many2one('ir.model.fields', 'Fields', domain=[('model','=','account.move.line')],
            help="Select which account filed you want export."),
        'field_indirection': fields.char('Indirection', size=128, help="Indirection line if fields is a key (ex : .name) "),
        'field_text': fields.char('Value', size=512, help="You can put here text (if 'Field type' on 'Text field') or python expression (if 'Field type' on 'Build field')."),
        'field_internal': fields.selection([
            ('journal_code','Target Journal code'),
            ('entry_num','# Entry (relatif)')], 'Computed field',
            help="Target Jounal Code: Journal code when you run wizard. '# Entry': Number of entry (relative to export)"),

        'build_cmd': fields.char('Build command', size=64, required=True,
            help="Define with folowing sample : \n \
                ['string','%s'] : For standard string field. \n \
                ['string','%20s'] : For right justify string on 20 char. \n \
                ['date','%d/%m/%Y'] : For date formated in french. \n \
                ['float','%f'], : ... \n \
                ['int','%d'] : ..."),
        'position': fields.integer('Position',required=True, help='Position in exported file (not use)'),
        'lenght': fields.integer('Size (lenght)', required=True, help='Lenght of field in exported file.'),
        'error_label': fields.char('Error label', size=64, help="Fill this information if the content of the field shouldn't empty. This information ..."),

        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'build_cmd': lambda *a: "['string','%s']",
        'type_field': lambda *a: 'internal_field',
        'field_text': lambda *a: '',
        'field_indirection': lambda *a: '',
        'position': lambda *a: 0,
        'active': lambda *a: True,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    _order = "sequence"

    def get_building_field(self, cr, uid, ids, context={}):
        """
        Return a list of informations need to build each field.
        """
        result = []
        for line in self.browse(cr, uid, ids, context):
            temp = []
            # Ajout du type de champs ...
            if line.type_field == 'account_field':
                temp.append([line.type_field,line.field_account.id,line.field_indirection or ''])
            elif line.type_field in ['text_field','build_field']:
                temp.append([line.type_field,line.field_text])
            else:
                temp.append([line.type_field,line.field_internal])
            # ... ajout des infos complémentaire, position, longueur, ...
            temp.extend([line.position,line.lenght,eval(line.build_cmd)])
            # ... ajout du libelé si besoin ...
            if line.error_label:
                temp.extend(line.error_label)
            result.append(temp)
        return result
asgard_ledger_export_fields()

class asgard_ledger_export_statement(osv.osv):
    """
    Liste des exports déja réalisé
    """
    def _balance(self, cursor, user, ids, name, attr, context=None):
        res = {}

        for statement in self.browse(cursor, user, ids, context=context):
            res[statement.id] = 0.0
            for ales_line_id in statement.ales_line_ids:
                if ales_line_id.debit > 0:
                    res[statement.id] += ales_line_id.debit
                else:
                    res[statement.id] -= ales_line_id.credit
            for r in res:
                res[r] = round(res[r], 2)
        return res

    def _get_period(self, cr, uid, context={}):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    _order = "date desc"
    _name = "asgard.ledger.export.statement"
    _description = "Asgard Ledger Export Statement"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'journal_period_id': fields.many2many('account.journal.period', 'asgard_export_ledger_journal_period_rel',
            'statement_id', 'journal_period_id', 'Journal/Period', readonly=True, states={'draft':[('readonly',False)]},
            help="Select which period you want export."),
        'ale_id': fields.many2one('asgard.ledger.export', 'Asgard Ledger', required=True, readonly=True,
            states={'draft':[('readonly', False)]}),
        'ales_line_ids': fields.one2many('asgard.ledger.export.statement.line', 'ales_id', 'ALE Lines',
            readonly=True, states={'draft':[('readonly',False)]}),
        'balance': fields.function(_balance, method=True, string='Balance'),
        'state': fields.selection([('draft', _('Draft')),('confirm', _('Confirm')),('done', _('Done')),('cancel', _('Cancel'))],
            'State', required=True,
            states={'confirm': [('readonly', True)]}, readonly="1"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'name': lambda self, cr, uid, context=None: \
                self.pool.get('ir.sequence').get(cr, uid, 'asgard.ledger.export.statement'),
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }

    def onchange_ale_id(self, cr, uid, ids, ale_id):
        if not ale_id:
            return {}

        ale_obj = self.pool.get('asgard.ledger.export')
        journal_period_obj = self.pool.get('account.journal.period')

        ale = ale_obj.browse(cr, uid, ale_id)
        journal_ids = [x.journal_id.id for x in ale.alej_line]

        journal_period_ids = journal_period_obj.search(cr, uid, [('journal_id','in',journal_ids)])

        return {'context':{'journal_id': journal_ids}}

    def action_confirm(self, cr, uid, ids, *args):
        result = False
        # Si la balance est égale a zéro et qu'il y a des lignes à exporter
        for ale in self.browse(cr, uid, ids, context={}):
            if len(ale.ales_line_ids) == 0:
                raise osv.except_osv(_('No Lines !'), _("You have to add some line to export."))
            if ale.balance == 0.0:
                result = self.write(cr, uid, ids, {'state':'confirm'})
            else:
                raise osv.except_osv(_('Bad balance !'), _("Balance need to be equal to zero."))
        return result


    def action_draft(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'draft'})

    def action_cancel(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'cancel'})

    def action_populate(self, cr, uid, ids, *args):
        """
        parameters :
            journal_period_id
        """
        pool = pooler.get_pool(cr.dbname)
        journal_period_obj = pool.get('account.journal.period')
        ales_line_obj = pool.get('asgard.ledger.export.statement.line')
        for ale in self.browse(cr, uid, ids, context={}):
            if not ale.journal_period_id:
                raise osv.except_osv(_('No Journal/Period selected !'), _('You have to select Journal/Period before populate line.'))
            jp_ids = journal_period_obj.read(cr, uid, map(lambda x:x.id,ale.journal_period_id), ['journal_id','period_id'])
            start = time.time()
            for jp in jp_ids:
                offset = 0
                results = [1]
                while len(results):
                    cr.execute('SELECT id \
                        FROM \
                            account_move_line \
                        WHERE \
                            period_id = %s AND journal_id = %s AND id NOT IN \
                            (SELECT move_line_id FROM asgard_ledger_export_statement_line) \
                        LIMIT 500 OFFSET %s',
                        (jp['period_id'][0],jp['journal_id'][0],str(offset)))
                    results = map(lambda x:x[0], cr.fetchall())
                    for result in results:
                        ales_line_id = ales_line_obj.create(cr, uid, {
                            'ales_id': ale.id,
                            'move_line_id': result})
            stop = time.time()
        return True

    def _fjournal_code(self, cr, uid, ids, **kwargs):
        alej_obj = pooler.get_pool(cr.dbname).get('asgard.ledger.export.journal')
        alej_line_id = alej_obj.search(cr, uid, [
            ('asgard_ledger_id', '=', kwargs['data'][1].ales_id.ale_id.id),
            ('journal_id', '=', kwargs['data'][1].journal_id.id),
            ('active', '=', True)])
        if not alej_line_id:
            raise osv.except_osv(_('No Journal linked !'), _("You have to define OpenERP journal linked with target name in asgard ledger configurations '%s'" % data))
        return alej_obj.read(cr, uid, alej_line_id, ['journal_name'])[0]['journal_name']

    def _faccount_field(self, cr, uid, ids, **kwargs):
        """
        Cette fonction peut être remplacée par '_fbuild_field', mais elle est
        gardé pour éviter d'avoir mettre une expression python pour les champs
        simple de l'écriture et leur indirection de niveau 1
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : Value of field
        """
        imf_obj = pooler.get_pool(cr.dbname).get('ir.model.fields')
        # Récupération du nom du champs par rapport à l'object 'ir_model_fields' ...
        imf = imf_obj.read(cr, uid, [kwargs['data'][1]], ['name'])[0]['name']
        # ... Contruction du champs et affectation à 'bf.
        t = "kwargs['line'].move_line_id.%s%s" % (str(imf),str(kwargs['data'][2]))
        if isinstance(eval(t),float):
            return str(eval(t))
        return eval(t)

    def _ftext_field(self, cr, uid, ids, **kwargs):
        """
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : Text value of data given in parameters
        """
        return kwargs['data'][1]

    def _fbuild_field(self, cr, uid, ids, **kwargs):
        """
        Evalue le champ contenant une expression Python
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : result of python expression evaluation.
        """
        result = False
        if kwargs['data'][1]:
            # Récupération de l'objet 'account_move_line'
            obj = kwargs['line'].move_line_id
            # Évaluation de l'expression python sur l'objet
            result = eval(kwargs['data'][1], {'object':obj, 'time':time})
        return result

    def _finternal_field(self, cr, uid, ids, **kwargs):
        """

        """
        return self.get_value(cr, uid, ids, data=[kwargs['data'][1], kwargs['line']])

    def get_value(self, cr, uid, ids, **kwargs):
        """
        Call correct method depend on parameters
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : result of method called
        """
        method_name = '_f' + str(kwargs['data'][0]).lower()
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print ("The method for verify '%s' type isn't defined (You must define it in class 'asgard_ledger_export_statement' of module '%s')." % (method_name,__name__))
        else:
            return method(cr, uid, ids, **kwargs)

    def action_export(self, cr, uid, ids, *args):
        """
        For each entry line build the text value
        """
        pool = pooler.get_pool(cr.dbname)
        mod_obj = self.pool.get('ir.model.data')
        ale_obj = pool.get('asgard.ledger.export')
        alej_obj = pool.get('asgard.ledger.export.journal')
        attach_obj = pool.get('ir.attachment')
        for ales in self.browse(cr, uid, ids):
            # Initalisation de l'encodage du fichier
            enc = generic_encode(
                file_header=ales.ale_id.file_header,
                separator=ales.ale_id.separator,
                ext=ales.ale_id.extension,
                ending=ale_obj.get_end_line(cr, uid, ales.ale_id.end_line),
                encoding=ales.ale_id.encoding)
            # Recupération du tableau de construction de ligne
            build_line = ale_obj.get_building_line(cr, uid, [ales.ale_id.id])
            # pour chaque ligne écritures
            for ales_line in ales.ales_line_ids:
                # Pour chaque construction de champs dans le tableau 'build_line'
                # Duplication du tableau de génération de ligne de texte
                bl = copy.deepcopy(build_line)
                for bf in bl:
                    bf[0] = self.get_value(cr, uid, ids, data=bf[0], line=ales_line)
                result = enc.write_file_in_flow(bl)
            ####
            ## Attachement
            # enc.export_file('addons/asgard_ledger_export/tmp')
            fp = open(os.path.join(enc.dir_tmp, enc.filetmp), 'r')
            file_data = fp.read()
            attach_id = attach_obj.create(cr, uid, {
                'name': 'export : ' + ales.name,
                'datas': base64.encodestring(file_data),
                'datas_fname': enc.filetmp,
                'res_model': 'asgard.ledger.export.statement',
                'res_id': ales.id, # Nom de l'objet auquel est attaché le document
                })
            ## Attachement
        self.write(cr, uid, ids, {'state':'done'})

        return True
#        res = mod_obj.get_object_reference(cr, uid, 'document', 'action_document_file_form')
#        res_id = res and res[1] or False
#        return {
#            'name': 'Attachments',
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'view_id': [res_id],
#            'res_model': 'ir.attachment',
#            'type': 'ir.actions.act_window',
#            'nodestroy': True,
#            'target': 'current',
#            'res_id': attach_id or False,
#        }

asgard_ledger_export_statement()

class asgard_ledger_export_statement_line(osv.osv):
    _name = "asgard.ledger.export.statement.line"
    _description = "Export Statement reconcile"
    _columns = {
        'name': fields.char('Date', size=64, translate=True, required=True, readonly=True),
        'ales_id': fields.many2one('asgard.ledger.export.statement', 'Asgard Statement', required=True, ondelete='cascade', select=True),
        'move_line_id': fields.many2one('account.move.line', 'Entry',
            select=True, required=True,
            help="Entry selected for ..."),
        'date_created': fields.related('move_line_id', 'date_created', type='date', string='Date Created Entry', store=True),
        'move_id': fields.related('move_line_id', 'move_id', type='many2one', relation='account.move', string='Entry', store=True),
        'period_id': fields.related('move_line_id', 'period_id', type='many2one', relation='account.period', string='Period', store=True),
        'journal_id': fields.related('move_line_id', 'journal_id', type='many2one', relation='account.journal', string='Journal', store=True),
        'credit':fields.related('move_line_id', 'credit', type='float', string='Credit', store=True),
        'debit':fields.related('move_line_id', 'debit', type='float', string='Debit', store=True),
        'account_id':fields.related('move_line_id','account_id', type='many2one', relation='account.account', string='Account', store=True),
        'text_line': fields.text('Line exported', readonly=True,
            help="Value of the line when it's exported in file (From format field)"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'name': lambda *a: time.strftime('%Y/%m/%d-%H:%M:%S'),
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    _order = 'name'
asgard_ledger_export_statement_line()