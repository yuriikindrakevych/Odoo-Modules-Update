odoo.define('website_sale_delivery_mobius.checkout', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale_delivery.checkout');

    var _t = core._t;

    publicWidget.registry.websiteSaleDelivery.include({
        /**
         * Override _handleCarrierUpdateResultBadge to add custom logic
         */
        _handleCarrierUpdateResultBadge: function (result) {
            var $carrierBadge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .o_wsale_delivery_badge_price');

            if (result.status === true) {
                if (result.is_free_delivery) {
                    $carrierBadge.text(_t('Free'));
                } else if (result.is_base_delivery) {
                    $carrierBadge.text(_t('Calculate'));
                } else {
                    $carrierBadge.html(result.new_amount_delivery);
                }
                $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
            } else {
                $carrierBadge.addClass('o_wsale_delivery_carrier_error');
                $carrierBadge.text(result.error_message);
            }
        }
    });
});
