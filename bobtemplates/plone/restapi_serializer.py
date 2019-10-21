# -*- coding: utf-8 -*-

from bobtemplates.plone.base import base_prepare_renderer
from bobtemplates.plone.base import git_commit
from bobtemplates.plone.base import remove_unwanted_files
from bobtemplates.plone.base import update_configure_zcml
from lxml import etree

import case_conversion as cc


def _update_package_configure_zcml(configurator):
    path = "{0}".format(configurator.variables["package_folder"])
    file_name = u"configure.zcml"
    match_xpath = "include[@package='.api']"
    match_str = "-*- extra stuff goes here -*-"
    insert_str = """
  <include package=".api" />
"""
    update_configure_zcml(
        configurator,
        path,
        file_name=file_name,
        match_xpath=match_xpath,
        match_str=match_str,
        insert_str=insert_str,
    )


def _update_api_configure_zcml(configurator):
    path = "{0}/api".format(configurator.variables["package_folder"])
    file_name = u"configure.zcml"
    example_file_name = "{0}.example".format(file_name)
    match_xpath = "zope:include[@package='.serializers']"
    match_str = "-*- extra stuff goes here -*-"
    insert_str = """
  <include package=".serializers" />
"""
    update_configure_zcml(
        configurator,
        path,
        file_name=file_name,
        example_file_name=example_file_name,
        match_xpath=match_xpath,
        match_str=match_str,
        insert_str=insert_str,
    )


def _update_serializers_configure_zcml(configurator):
    path = "{0}/api/serializers".format(configurator.variables["package_folder"])
    file_name = u"configure.zcml"
    example_file_name = "{0}.example".format(file_name)
    match_xpath = "zope:include[@package='.{0}']".format(
        configurator.variables["serializer_class_name_normalized"]
    )
    match_str = "-*- extra stuff goes here -*-"
    insert_str = '<include package=".{0}" />\n'.format(
        configurator.variables["serializer_class_name_normalized"]
    )
    update_configure_zcml(
        configurator,
        path,
        file_name=file_name,
        example_file_name=example_file_name,
        match_xpath=match_xpath,
        match_str=match_str,
        insert_str=insert_str,
    )


def _update_metadata_xml(configurator):
    """ Add plone.restapi dependency metadata.xml in
        Generic Setup profiles.
    """
    metadata_file_name = u"metadata.xml"
    metadata_file_dir = u"profiles/default"
    metadata_file_path = (
        configurator.variables["package_folder"]
        + "/"
        + metadata_file_dir
        + "/"
        + metadata_file_name
    )

    with open(metadata_file_path, "r") as xml_file:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file, parser)
        dependencies = tree.xpath("/metadata/dependencies")[0]
        dep = "profile-plone.restapi:default"
        dep_exists = False
        for e in dependencies.iter("dependency"):
            dep_name = e.text
            if dep_name == dep:
                dep_exists = True

        if dep_exists:
            print("{dep} already in metadata.xml, skip adding!".format(dep=dep))
            return
        dep_element = etree.Element("dependency")
        dep_element.text = dep
        dependencies.append(dep_element)

    with open(metadata_file_path, "wb") as xml_file:
        tree.write(xml_file, pretty_print=True, xml_declaration=True, encoding="utf-8")


def _remove_unwanted_files(configurator):
    file_paths = []
    rel_file_paths = [
        "/api/configure.zcml.example",
        "/api/serializers/configure.zcml.example",
    ]
    base_path = configurator.variables["package_folder"]
    for rel_file_path in rel_file_paths:
        file_paths.append("{0}{1}".format(base_path, rel_file_path))
    remove_unwanted_files(file_paths)


def pre_renderer(configurator):
    """Pre rendering."""
    configurator = base_prepare_renderer(configurator)
    configurator.variables["template_id"] = "restapi_serializer"
    class_name = configurator.variables["serializer_class_name"].strip("_")
    configurator.variables["serializer_class_name"] = cc.pascalcase(class_name)
    configurator.variables["serializer_class_name_normalized"] = cc.snakecase(
        class_name
    )
    configurator.target_directory = configurator.variables["package_folder"]


def post_renderer(configurator):
    """Post rendering."""
    _update_package_configure_zcml(configurator)
    _update_api_configure_zcml(configurator)
    _update_serializers_configure_zcml(configurator)
    _update_metadata_xml(configurator)
    _remove_unwanted_files(configurator)
    git_commit(
        configurator,
        "Add restapi_serializer: {0}".format(configurator.variables["serializer_class_name"]),
    )
