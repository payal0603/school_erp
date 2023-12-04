odoo.define('odoo-debrand-11.custom_user_menu', function (require) {
    "use strict";

    var UserMenu = require('web.UserMenu');

    UserMenu.include({
        init: function () {
            this._super.apply(this, arguments);
            // Remove the menu item with the specified action ID
            var menuActionIdToRemove = 'shortcuts';
            this._removeMenuItem(menuActionIdToRemove);
        },

        _removeMenuItem: function (actionId) {
            var menuItems = this._getMenuItems();
            for (var i = menuItems.length - 1; i >= 0; i--) {
                if (menuItems[i].action === actionId) {
                    menuItems.splice(i, 1);
                    break;
                }
            }
        },

        _getMenuItems: function () {
            var menuData = this.getSession().user_menu;
            return menuData.children;
        },
    });

});
