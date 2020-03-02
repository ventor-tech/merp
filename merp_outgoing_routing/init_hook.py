# Copyright 2020 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    Without this script, big databases can take a long time to install this
    module.
    """
    set_stock_location_priority_default(cr)
    set_stock_quant_location_priority_default(cr)


def set_stock_location_priority_default(cr):
    cr.execute(
        """SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_location' AND
    column_name='removal_prio'"""
    )
    if not cr.fetchone():
        logger.info("Creating field removal_prio on stock_location")
        cr.execute(
            """
            ALTER TABLE stock_location
            ADD COLUMN removal_prio integer
            DEFAULT 0;
            """
        )


def set_stock_quant_location_priority_default(cr):
    cr.execute(
        """SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_quant' AND
    column_name='removal_prio'"""
    )
    if not cr.fetchone():
        logger.info("Creating field removal_prio on stock_quant")
        cr.execute(
            """
            ALTER TABLE stock_quant
            ADD COLUMN removal_prio integer
            DEFAULT 0;
            """
        )
