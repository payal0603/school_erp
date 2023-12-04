odoo.define('debrand_web.remove_logo', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var core = require('web.core');
    var qweb = core.qweb;

    WebClient.include({
        show_application: function () {
            this._super.apply(this, arguments);
            qweb.add_template('/debrand_web/static/src/xml/custom_template.xml');
        },
    });
});
