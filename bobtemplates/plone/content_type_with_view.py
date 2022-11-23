# -*- coding: utf-8 -*-
"""Generate content_type_with_view."""

from mrbob.rendering import jinja2_env
import ast
import pprint
from bobtemplates.plone.base import (
    CONTENT_TYPE_INTERFACES,
    ZCML_NAMESPACES,
    base_prepare_renderer,
    echo,
    git_commit,
    update_file,
)
from bobtemplates.plone.utils import run_black, run_isort
from bobtemplates.plone import view
from bobtemplates.plone import content_type

def mypprint(value):
    return pprint.pformat(value)

jinja2_env.filters["mypprint"] = mypprint

def prepare_renderer(configurator):
    """Prepare rendering."""
    configurator.variables["my_schema"] = ast.literal_eval(configurator.variables["my_schema"])
    content_type.prepare_renderer(configurator)
    view.prepare_renderer(configurator)

def post_renderer(configurator):
    """Post rendering."""
    content_type.post_renderer(configurator)
    content_type._update_types_xml(configurator)
    content_type._update_parent_types_fti_xml(configurator)
    content_type._update_permissions_zcml(configurator)
    content_type._update_rolemap_xml(configurator)
    content_type._update_metadata_xml(configurator)
    view._update_configure_zcml(configurator)
    view._update_views_configure_zcml(configurator)
    view._delete_unwanted_files(configurator)
    run_isort(configurator)
    run_black(configurator)
    git_commit(
        configurator,
        "Add content type with view: {0} - {1}".format(
            configurator.variables["dexterity_type_name"],
            configurator.variables["view_name"],
        ),
    )
