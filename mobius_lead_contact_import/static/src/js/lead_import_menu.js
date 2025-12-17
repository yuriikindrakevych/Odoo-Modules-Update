odoo.define('mobius_lead_contact_import.LeadContactsImportMenu', function (require) {
    "use strict";

    const FavoriteMenu = require('web.FavoriteMenu');
    const { Component } = owl;

    class LeadContactsImportMenu extends Component {
        importRecords() {
            const action = {
                type: 'ir.actions.client',
                tag: 'import',
                params: {
                    model: 'res.partner',
                    context: {
                        import_lead: true // lead import context
                    }
                }
            };
            this.trigger('do-action', { action });
        }

        static shouldBeDisplayed(env) {
            return env.view &&
                ['kanban', 'list'].includes(env.view.type) &&
                env.action.res_model === 'res.partner';  // Only for res.partner
        }
    }

    LeadContactsImportMenu.template = 'mobius_lead_contact_import.LeadContactsImportRecords';
    FavoriteMenu.registry.add('lead-contacts-import-menu', LeadContactsImportMenu, 2);
    console.log("hello")

    return LeadContactsImportMenu;
});
