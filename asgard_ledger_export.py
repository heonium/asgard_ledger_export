# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2005-2008, Héonium SARL - Tous droits réservés
#               Christophe CRIER <contact@heonium.com> (http://heonium.com)
#
# Ce logiciel est régi par la licence CeCILL soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant 
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.
###############################################################################

import os
import base64
import copy
import time
import pooler
from osv import fields, osv
from hnm_common.hnm_common_lib import *

##########
### asgard_coala_plugin.configuration
class asgard_ledger_export(osv.osv):
    """
    Table d'association entre les journaux comptable d'OpenERP et les noms des 
    journaux de Coala Compta.
    """
    _name = "asgard.ledger.export"
    _description = "Define export"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True),
        'separator': fields.char('Separator', size=1, help="Separator field, leave blank if you dont have"),
        'end_line': fields.selection([('\n', 'Unix'), ('\n\r','Windows')], 'End of line'),
        'extension': fields.char('Extension', size=5, help="String add on end of name file (without the dot).", required=True),
        'alej_line': fields.one2many('asgard.ledger.export.journal', 'asgard_ledger_id', 'Asgard Ledger Journal Lines'),
        'alef_line': fields.one2many('asgard.ledger.export.fields', 'asgard_ledger_id', 'Asgard Ledger Field Lines'),
        'active': fields.boolean('Active'),
    }
    _defaults = {
        'active': lambda *a: True,
        'end_line': lambda *a: '\n',
        'extension': lambda *a: 'csv'
    }

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
    _description = "Link beetwenn OpenERP's journal and Sage Coala journal"
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True),
        'asgard_ledger_id': fields.many2one('asgard.ledger.export', 'Asgard Ledger Ref', required=True, ondelete="cascade", select=True,
            help="Associated configuration"),
        'active': fields.boolean('Active'),
        # Association journaux
        'journal_name': fields.char('Journal name', size=3, required=True,
            help="Journal name in target software. Warning, you must put exact name"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, ondelete="cascade",
            help="Select the associated OpenERP's journal"),
    }
    _defaults = {
        'active': lambda *a: True,
    }
    _sql_constraints = [
        ('oerp_journal_uniq', 'unique (asgard_ledger_id,journal_id)', 'Il existe déjà une association avec ce journal !'),
        ('target_journal_uniq', 'unique (asgard_ledger_id,journal_name)', 'Il existe déjà une association avec ce journal (nom cible)!'),
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
            ('internal_field','Internal field')], 'Field type',
                help="Select the type of field\n \
                    Account field : Field of object 'Account'.\n \
                    Internal field : Select field from list.\n \
                    Text field : Only text."),
        
        'field_account': fields.many2one('ir.model.fields', 'Fields', domain=[('model','=','account.move.line')],
            help="Select which account filed you want export."),
        'field_indirection': fields.char('Indirection', size=128, help="Indirection line if fields is a key (ex : .name) "),
        'field_text': fields.char('Text', size=64),
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
    }
    _defaults = {
        'build_cmd': lambda *a: "['string','%s']",
        'type_field': lambda *a: 'internal_field',
        'field_indirection': lambda *a: '',
        'position': lambda *a: 0,
        'active': lambda *a: True,
    }
    _order = "sequence"

    def get_building_field(self, cr, uid, ids, context={}):
        """
        Return build line for id
        """
        result = []
        for line in self.browse(cr, uid, ids, context):
            temp = []
            # Ajout du type de champs ...
            if line.type_field == 'account_field':
                temp.append([line.type_field,line.field_account.id,line.field_indirection or ''])
            elif line.type_field == 'text_field':
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
        'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirm'),('cancel', 'Cancel')],
            'State', required=True,
            states={'confirm': [('readonly', True)]}, readonly="1"),
    }
    _defaults = {
        'name': lambda self, cr, uid, context=None: \
                self.pool.get('ir.sequence').get(cr, uid, 'asgard.ledger.export.statement'),
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }

    def action_confirm(self, cr, uid, ids, *args):
        result = False
        # Si la balance est égale a zéro
        for ale in self.browse(cr, uid, ids, context={}):
            if ale.balance == 0.0:
                result = self.write(cr, uid, ids, {'state':'confirm'})
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
                        offset+=1
        return True

    def action_export(self, cr, uid, ids, *args):
        """
        For each line build the text value
        """
        pool = pooler.get_pool(cr.dbname)
        ale_obj = pool.get('asgard.ledger.export')
        alej_obj = pool.get('asgard.ledger.export.journal')
        imf_obj = pool.get('ir.model.fields')
        attach_obj = pool.get('ir.attachment')
        for ales in self.browse(cr, uid, ids, context={}):
            enc = generic_encode(ales.ale_id.separator,ales.ale_id.extension,ales.ale_id.end_line)
            # Recupération du tableau de construction de ligne
            build_line = ale_obj.get_building_line(cr, uid, [ales.ale_id.id])
            #print "[HNM]|",__name__,"|action_export|build_line:",build_line
            for ales_line in ales.ales_line_ids:
                # Pour chaque construction de champs dans le tableau 'build_line'
                # Duplication du tableau de génération de ligne
                bl = copy.deepcopy(build_line)
                for bf in bl:
# [TODO] Amméliorer la sélection de champs, une fonction dans l'objet 'asgard_ledger_export_fields' ?
                    # Définir le premier champs
                    if bf[0][0] == 'text_field':
                        bf[0] = bf[0][1]
                        #print "[HNM]|",__name__,"|action_export|build_line:",build_line
                    elif bf[0][0] == 'internal_field':
                        if bf[0][1] == 'journal_code':
                            alej_line_id = alej_obj.search(cr, uid, [
                                ('asgard_ledger_id', '=', ales.ale_id.id),
                                ('journal_id', '=', ales_line.journal_id.id),
                                ('active', '=', True)])
                            if not alej_line_id:
                                raise osv.except_osv(_('No Journal linked !'), _("You have to define OpenERP journal linked with target name in asgard ledger configurations '%s'" % ales_line.journal_id.name))
                            bf[0] = alej_obj.read(cr, uid, alej_line_id, ['journal_name'])[0]['journal_name']
                    else:
                        # Récupération du nom du champs par rapport à l'object 'ir_model_fields' ...
                        imf = imf_obj.read(cr, uid, [bf[0][1]], ['name'])[0]['name']
                        # ... Contruction du champs et affectation à 'bf.
                        t = 'ales_line.move_line_id.' + str(imf) + str(bf[0][2])
                        if isinstance(eval(t),float):
                            bf[0] = str(eval(t))
                        else:
                            bf[0] = eval(t)
                result = enc.write_file_in_flow(bl)
            ####
            ## Attachement
            # enc.export_file('addons/asgard_ledger_export/tmp')
            fp = open(os.path.join(enc.dir_tmp, enc.fileTmp), 'r')
            file_data = fp.read()
            attach_obj.create(cr, uid, {
                'name': 'export : ' + ales.name,
                'datas': base64.encodestring(file_data),
                'datas_fname': enc.fileTmp,
                'res_model': 'asgard.ledger.export.statement',
                'res_id': ales.id, # Nom de l'objet auquel est attaché le document
                })
            ## Attachement
        return True
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
        'date_created': fields.related('move_line_id', 'date_created', type='date', string='Date Created Entry'),
        'move_id': fields.related('move_line_id', 'move_id', type='many2one', relation='account.move', string='Entry'),
        'period_id': fields.related('move_line_id', 'period_id', type='many2one', relation='account.period', string='Period'),
        'journal_id': fields.related('move_line_id', 'journal_id', type='many2one', relation='account.journal', string='Journal'),
        'credit':fields.related('move_line_id', 'credit', type='float', string='Credit'),
        'debit':fields.related('move_line_id', 'debit', type='float', string='Debit'),
        'account_id':fields.related('move_line_id','account_id', type='many2one', relation='account.account', string='Account'),
        'text_line': fields.text('Line exported', readonly=True,
            help="Value of the line when it's exported in file (From format field)")
    }
    _defaults = {
        'name': lambda *a: time.strftime('%Y/%m/%d-%H:%M:%S'),
    }
    _order = 'name'
asgard_ledger_export_statement_line()