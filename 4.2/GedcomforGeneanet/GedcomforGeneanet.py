#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012  Bastien Jacquet
# Copyright (C) 2012  Doug Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: $

"""
Extends GedcomWriter to include common non-compliant GEDCOM additions.
"""
#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import time
import io

#------------------------------------------------------------------------
#
# GTK modules
#
#------------------------------------------------------------------------
from gramps.version import VERSION
from gi.repository import Gtk
import gramps.plugins.lib.libgedcom as libgedcom
from gramps.plugins.export import exportgedcom
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.errors import DatabaseError
from gramps.gen.lib import (EventRoleType, FamilyRelType, EventType, Person, AttributeType)
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.file import media_path_full,media_path,relative_path
try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext
import zipfile
import logging
LOG = logging.getLogger(".gedcomforgeneanet")


MIME2GED = {
    "image/bmp"   : "bmp",
    "image/gif"   : "gif",
    "image/jpeg"  : "jpeg",
    "image/x-pcx" : "pcx",
    "image/tiff"  : "tiff",
    "audio/x-wav" : "wav"
    }

LANGUAGES = {
    'cs' : 'Czech',     'da' : 'Danish',    'nl' : 'Dutch',
    'en' : 'English',   'eo' : 'Esperanto', 'fi' : 'Finnish',
    'fr' : 'French',    'de' : 'German',    'hu' : 'Hungarian',
    'it' : 'Italian',   'lt' : 'Latvian',   'lv' : 'Lithuanian',
    'no' : 'Norwegian', 'po' : 'Polish',    'pt' : 'Portuguese',
    'ro' : 'Romanian',  'sk' : 'Slovak',    'es' : 'Spanish',
    'sv' : 'Swedish',   'ru' : 'Russian',
    }

#-------------------------------------------------------------------------
#
# sort_handles_by_id
#
#-------------------------------------------------------------------------
def sort_handles_by_id(handle_list, handle_to_object):
    """
    Sort a list of handles by the Gramps ID. 
    
    The function that returns the object from the handle needs to be supplied 
    so that we get the right object.
    
    """
    sorted_list = []
    for handle in handle_list:
        obj = handle_to_object(handle)
        if obj:
            data = (obj.get_gramps_id(), handle)
            sorted_list.append (data)
    sorted_list.sort()
    return sorted_list


class GedcomWriterforGeneanet(exportgedcom.GedcomWriter):
    """
    GedcomWriter forGeneanets.
    """
    def __init__(self, database, user, option_box=None):
        super(GedcomWriterforGeneanet, self).__init__(database, user, option_box)
        if option_box:
            # Already parsed in GedcomWriter
            self.include_witnesses = option_box.include_witnesses
            self.include_media = option_box.include_media
            self.relativepath = option_box.relativepath
            self.include_depot = option_box.include_depot
            self.geneanet_obsc = option_box.geneanet_obsc
        else:
            self.include_witnesses = 1
            self.include_media = 1
            self.include_depot = 1
            self.geneanet_obsc = 0
            self.relativepath = 0
        self.zipfile = None

    def get_filtered_database(self, dbase, progress=None, preview=False):
        """
        dbase - the database
        progress - instance that has:
           .reset() method
           .set_total() method
           .update() method
           .progress_cnt integer representing N of total done
        """
        # Increment the progress count for each filter type chosen
        if self.private and progress:
            progress.progress_cnt += 1

        if self.restrict_num > 0 and progress:
            progress.progress_cnt += 1

        if (self.cfilter != None and (not self.cfilter.is_empty())) and progress:
            progress.progress_cnt += 1

        if (self.nfilter != None and (not self.nfilter.is_empty())) and progress:
            progress.progress_cnt += 1

        if self.reference_num > 0 and progress:
            progress.progress_cnt += 1
        if progress:
            progress.set_total(progress.progress_cnt)
            progress.progress_cnt = 0

        if self.preview_dbase:
            if progress:
                progress.progress_cnt += 5
            return self.preview_dbase

        self.proxy_dbase.clear()
        for proxy_name in self.get_proxy_names():
            LOG.debug("proxy %s" % proxy_name)
            dbase = self.apply_proxy(proxy_name, dbase, progress)
            if preview:
                self.proxy_dbase[proxy_name] = dbase
                self.preview_proxy_button[proxy_name].set_sensitive(1)
                people_count = len(dbase.get_person_handles())
                self.preview_proxy_button[proxy_name].set_label(
                    # translators: leave all/any {...} untranslated
                    ngettext("{number_of} Person",
                             "{number_of} People", people_count
                            ).format(number_of=people_count) )
        return dbase



    
    def _photo(self, photo, level):
        """
        Overloaded media-handling method to skip over media
        if not included.
        """
        LOG.debug("deb photo %d" % self.relativepath)
        if self.include_media:
            photo_obj_id = photo.get_reference_handle()
            photo_obj = self.dbase.get_object_from_handle(photo_obj_id)
            if photo_obj:
                mime = photo_obj.get_mime_type()
                form = MIME2GED.get(mime, mime)
                if self.relativepath:
                    fullpath = media_path_full(self.dbase, photo_obj.get_path())
                    if not os.path.isfile(fullpath):
                        return
                    base = media_path(self.dbase)
                    path = relative_path(fullpath,base)
                else:
                    path = media_path_full(self.dbase, photo_obj.get_path())
                    if not os.path.isfile(path):
                        return
                self._writeln(level, 'OBJE')
                if form:
                    self._writeln(level+1, 'FORM', form)
                self._writeln(level+1, 'TITL', photo_obj.get_description())
                self._writeln(level+1, 'FILE', path, limit=255)
                self._note_references(photo_obj.get_note_list(), level+1)
                self._packzip(path)
 
 
    def _packzip(self, path ):
        if path:
            toto = 0
          #  self.zipfile.write(path)

    def _family_events(self, family):
        super(GedcomWriterforGeneanet, self)._family_events(family)
        level = 1
#        self._writeln(level,"TEST")
        if (int(family.get_relationship()) == FamilyRelType.UNMARRIED or int(family.get_relationship()) == FamilyRelType.UNKNOWN):
            self._writeln(level, "_UST", "COHABITATION")
    
# Workaround pour geneanet upload
#    def _url_list(self, obj, level):
#        if self.include_persurl:
#            for url in obj.get_url_list():
#                self._writeln(level, 'OBJE')
#                self._writeln(level+1, 'FORM', 'URL')
#                if url.get_description():
#                    self._writeln(level+1, 'TITL', url.get_description())
#                if url.get_path():
#                    self._writeln(level+1, 'FILE', url.get_path(), limit=255)
#        else:
#            return

    def _process_family_event(self, event, event_ref):
        """
        Write the witnesses associated with the family event.
        based on http://www.geneanet.org/forum/index.php?topic=432352.0&lang=fr
        """
        super(GedcomWriterforGeneanet, self)._process_family_event(event,\
                                                                 event_ref)
        if self.include_witnesses:
            for (objclass, handle) in self.dbase.find_backlink_handles(
                event.handle, ['Person']):
                person = self.dbase.get_person_from_handle(handle)
                if person:
                    for ref in person.get_event_ref_list():
                        if ref.ref == event.handle:
                            if int(ref.get_role()) in [EventRoleType.WITNESS,EventRoleType.CELEBRANT,\
                        EventRoleType.INFORMANT,\
                             EventRoleType.CLERGY, EventRoleType.AIDE, EventRoleType.CUSTOM]:
                                level = 2
                                self._writeln(level, "ASSO", "@%s@" % person.get_gramps_id())
                                self._writeln(level+1, "TYPE", "INDI")
                                self._writeln(level+1, "RELA", "Witness")
                                self._note_references(ref.get_note_list(), level+1)

    def _sources(self):
        """
        Write out the list of sources, sorting by Gramps ID.
        """
        self.reset(_("Writing sources"))
        self.progress_cnt += 1
        self.update(self.progress_cnt)
        sorted_list = sort_handles_by_id(self.dbase.get_source_handles(),
                                         self.dbase.get_source_from_handle)

        for (source_id, handle) in sorted_list:
            source = self.dbase.get_source_from_handle(handle)
            if source is None: continue
            self._writeln(0, '@%s@' % source_id, 'SOUR')
            if source.get_title():
                if self.geneanet_obsc:
                    title = source.get_title()
                    ntitle = title.replace("généanet","g3n3an3t")
                    n2title = ntitle.replace("geneanet","g3n3an3t")
                    self._writeln(1, 'TITL', n2title)
                else:
                    self._writeln(1, 'TITL', source.get_title())

            if source.get_author():
                self._writeln(1, "AUTH", source.get_author())

            if source.get_publication_info() and not self.geneanet_obsc:
                self._writeln(1, "PUBL", source.get_publication_info())

            if source.get_abbreviation():
                self._writeln(1, 'ABBR', source.get_abbreviation())

            self._photos(source.get_media_list(), 1)

            if self.include_depot:
                for reporef in source.get_reporef_list():
                    self._reporef(reporef, 1)
                    break

            self._note_references(source.get_note_list(), 1)
            self._change(source.get_change_time(), 1)

 
    def _person_event_ref(self, key, event_ref):
        """
        Write the witnesses associated with the birth and death event. 
        based on http://www.geneanet.org/forum/index.php?topic=432352.0&lang=fr
        """
        super(GedcomWriterforGeneanet, self)._person_event_ref(key,event_ref)
        if self.include_witnesses and event_ref:
            role = int(event_ref.get_role())
            if role != EventRoleType.PRIMARY:
                return
            event = self.dbase.get_event_from_handle(event_ref.ref)
            etype = int(event.get_type())
            devel = 2
#            self._writeln(devel , "DEBUG NAISS OR DEATH TYPE", "@%s@" % etype)
#            self._writeln(devel , "DEBUG NAISS OR DEATH ROLE", "@%s@" % role)
            for (objclass, handle) in self.dbase.find_backlink_handles(
                event.handle, ['Person']):
                person = self.dbase.get_person_from_handle(handle)
                if person:
                    for ref in person.get_event_ref_list():
                        devel = 2
#                        self._writeln(devel , "DEBUG  ", "@%s@" % int(ref.get_role()))
                        if (ref.ref == event.handle): 
                            if int(ref.get_role()) in [EventRoleType.WITNESS,EventRoleType.CELEBRANT, EventRoleType.INFORMANT, EventRoleType.AIDE ,EventRoleType.CLERGY, EventRoleType.AIDE,EventRoleType.CUSTOM]:
                                level = 2
                                self._writeln(level, "ASSO", "@%s@" % person.get_gramps_id())
                                self._writeln(level+1, "TYPE", "INDI")
                                self._writeln(level+1, "RELA", "Witness")
                                self._note_references(ref.get_note_list(), level+1)

    def _process_person_event(self, person ,event ,event_ref):
        """
        Write the witnesses associated with other personnal event. 
        """
        super(GedcomWriterforGeneanet, self)._process_person_event(person , event , event_ref)
        etype = int(event.get_type())
        # if the event is a birth or death, skip it.
        if etype in (EventType.BIRTH, EventType.DEATH, EventType.MARRIAGE):
            return
        role = int(event_ref.get_role())
        if role != EventRoleType.PRIMARY:
            return
#        devel = 2
#        self._writeln(devel, "DEBUG EVEN TYPE", "@%s@" % etype)
#        self._writeln(devel, "DEBUG EVEN ROLE", "@%s@" % role)
        if self.include_witnesses:
            if etype in (EventType.BAPTISM, EventType.CHRISTEN):
#                self._writeln(devel , "DEBUG BAPT ROLE", "@%s@" % role)
                for (objclass, handle) in self.dbase.find_backlink_handles(
                    event.handle, ['Person']):
                    person2 = self.dbase.get_person_from_handle(handle)
                    if person2 and person2 != person:
                        for ref in person2.get_event_ref_list():
                            if (ref.ref == event.handle):
                                if (int(ref.get_role()) == EventRoleType.CUSTOM):
                                    level = 1
                                    self._writeln(level, "ASSO", "@%s@" % person2.get_gramps_id())
                                    self._writeln(level+1, "TYPE", "INDI")
                                    if person2.get_gender() == Person.MALE:
                                        self._writeln(level+1, "RELA", "Godfather")
                                    elif person2.get_gender() == Person.FEMALE:
                                        self._writeln(level+1, "RELA", "Godmother")
                                    else:
                                        self._writeln(level+1, "RELA", "Unknown")

                                    self._note_references(ref.get_note_list(), level+1)
                                else:
                                    level = 2
                                    self._writeln(level, "ASSO", "@%s@" % person2.get_gramps_id())
                                    self._writeln(level+1, "TYPE", "INDI")
                                    self._writeln(level+1, "RELA", "Witness")
                                    self._note_references(ref.get_note_list(), level+1)
            else:
                devel = 2
#                self._writeln(devel , "DEBUG NON BAPT ", "@%s@" % etype)
                for (objclass, handle) in self.dbase.find_backlink_handles(
                    event.handle, ['Person']):
                    person2 = self.dbase.get_person_from_handle(handle)
                    if person2 and person != person2:
                        for ref in person2.get_event_ref_list():
                            if (ref.ref == event.handle):  
                                if int(ref.get_role()) in [EventRoleType.WITNESS, EventRoleType.CELEBRANT, EventRoleType.INFORMANT, EventRoleType.AIDE, EventRoleType.CLERGY, EventRoleType.AIDE, EventRoleType.CUSTOM]:
#                                self._writeln(devel , "DEBUG NON BAPT 2 ", "@%s@" % int(ref.get_role()))
                                    level = 2
#pylint: disable=maybe-no-member
                                    self._writeln(level, "ASSO", "@%s@" % person2.get_gramps_id())
                                    self._writeln(level+1, "TYPE", "INDI")
                                    self._writeln(level+1, "RELA", "Witness")
                                    self._note_references(ref.get_note_list(), level+1)

    def _attributes(self, person):
        """
        Write out the attributes to the GEDCOM file.
        
        Since we have already looked at nicknames when we generated the names,
        we filter them out here.

        We use the GEDCOM 5.5.1 FACT command to write out attributes not
        built in to GEDCOM.

        """

        if person.get_privacy():
            self._writeln(1, '_PRIV')
            
        # filter out the nicknames
        attr_list = [attr for attr in person.get_attribute_list()
                      if attr.get_type() != AttributeType.NICKNAME]

        for attr in attr_list:

            attr_type = int(attr.get_type())
            name = libgedcom.PERSONALCONSTANTATTRIBUTES.get(attr_type)
            key = str(attr.get_type())
            value = attr.get_value().strip().replace('\r', ' ')

            if key in ("AFN", "RFN", "REFN", "_UID", "_FSFTID"):
#pylint: disable=maybe-no-member
                self._writeln(1, key, value)
                continue

            if key == "RESN":
                self._writeln(1, 'RESN')
                continue

            if name and name.strip():
                self._writeln(1, name, value)
            elif value:
                if not key == "ID Gramps fusionné":
#pylint: disable=maybe-no-member
                    self._writeln(1, 'FACT', value)
                    self._writeln(2, 'TYPE', key)
            else:
                continue
            self._note_references(attr.get_note_list(), 2)
            self._source_references(attr.get_citation_list(), 2)

    def _header(self, filename):
        """
        Write the GEDCOM header. 

            HEADER:=
            n HEAD {1:1}
            +1 SOUR <APPROVED_SYSTEM_ID> {1:1} 
            +2 VERS <VERSION_NUMBER> {0:1} 
            +2 NAME <NAME_OF_PRODUCT> {0:1} 
            +2 CORP <NAME_OF_BUSINESS> {0:1}           # Not used
            +3 <<ADDRESS_STRUCTURE>> {0:1}             # Not used
            +2 DATA <NAME_OF_SOURCE_DATA> {0:1}        # Not used
            +3 DATE <PUBLICATION_DATE> {0:1}           # Not used
            +3 COPR <COPYRIGHT_SOURCE_DATA> {0:1}      # Not used
            +1 DEST <RECEIVING_SYSTEM_NAME> {0:1*}     # Not used
            +1 DATE <TRANSMISSION_DATE> {0:1} 
            +2 TIME <TIME_VALUE> {0:1} 
            +1 SUBM @XREF:SUBM@ {1:1} 
            +1 SUBN @XREF:SUBN@ {0:1} 
            +1 FILE <FILE_NAME> {0:1} 
            +1 COPR <COPYRIGHT_GEDCOM_FILE> {0:1} 
            +1 GEDC {1:1}
            +2 VERS <VERSION_NUMBER> {1:1} 
            +2 FORM <GEDCOM_FORM> {1:1} 
            +1 CHAR <CHARACTER_SET> {1:1} 
            +2 VERS <VERSION_NUMBER> {0:1} 
            +1 LANG <LANGUAGE_OF_TEXT> {0:1} 
            +1 PLAC {0:1}
            +2 FORM <PLACE_HIERARCHY> {1:1} 
            +1 NOTE <GEDCOM_CONTENT_DESCRIPTION> {0:1} 
            +2 [CONT|CONC] <GEDCOM_CONTENT_DESCRIPTION> {0:M}
        
        """
        local_time = time.localtime(time.time())
        (year, mon, day, hour, minutes, sec) = local_time[0:6]
        date_str = "%d %s %d" % (day, libgedcom.MONTH[mon], year)
        time_str = "%02d:%02d:%02d" % (hour, minutes, sec)
        rname = self.dbase.get_researcher().get_name()
        LOG.debug("deb header %d" % self.relativepath)
        self._writeln(0, "HEAD")
        self._writeln(1, "SOUR", "Gramps")
        self._writeln(2, "VERS",  VERSION)
        self._writeln(2, "NAME", "Gramps")
        self._writeln(1, "DATE", date_str)
        self._writeln(2, "TIME", time_str)
        self._writeln(1, "SUBM", "@SUBM@")
        if self.relativepath:
            filenam = os.path.basename(filename)
            self._writeln(1, "FILE2", filenam, limit=255)
        else:
            self._writeln(1, "FILE", filename, limit=255)
        self._writeln(1, "COPR", 'Copyright (c) %d %s.' % (year, rname))
        self._writeln(1, "GEDC")
        self._writeln(2, "VERS", "5.5.1")
        self._writeln(2, "FORM", 'LINEAGE-LINKED')
        self._writeln(1, "CHAR", "UTF-8")

        # write the language string if the current LANG variable 
        # matches something we know about.

        lang = glocale.language[0]
        if lang and len(lang) >= 2:
            lang_code = LANGUAGES.get(lang[0:2])
            if lang_code:
                self._writeln(1, 'LANG', lang_code)


#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#
# GedcomWriter Options
#
#-------------------------------------------------------------------------
class GedcomWriterOptionBox(WriterOptionBox):
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options.
    """
    def __init__(self, person, dbstate, uistate):
        """
        Initialize the local options.
        """
        super(GedcomWriterOptionBox, self).__init__(person, dbstate, uistate)
        self.include_witnesses = 1
        self.include_witnesses_check = None
        self.include_media = 1
        self.include_media_check = None
        self.include_depot = 1
        self.include_depot_check = None
        self.geneanet_obsc = 0
        self.geneanet_obsc_check = None
        self.relativepath = 0
        self.relativepath_check = None

    def get_option_box(self):
        option_box = super(GedcomWriterOptionBox, self).get_option_box()
        # Make options:
        self.include_witnesses_check = Gtk.CheckButton(_("Include witnesses"))
        self.include_media_check = Gtk.CheckButton(_("Include media"))
        self.relativepath_check = Gtk.CheckButton(_("Relative path for media"))
        self.include_depot_check = Gtk.CheckButton(_("Include depot"))
        self.geneanet_obsc_check = Gtk.CheckButton(_("Geneanet obscufucation"))
        self.include_witnesses_check.set_active(1)
        self.include_media_check.set_active(1)
        self.include_depot_check.set_active(1)
        self.relativepath_check.set_active(0)
        self.geneanet_obsc_check.set_active(0)

        # Add to gui:
        option_box.pack_start(self.include_witnesses_check, False, False, 0)
        option_box.pack_start(self.include_media_check, False, False, 0)
        option_box.pack_start(self.include_depot_check, False, False, 0)
        option_box.pack_start(self.relativepath_check, False, False, 0)
        option_box.pack_start(self.geneanet_obsc_check, False, False, 0)
        return option_box

    def parse_options(self):
        """
        Get the options and store locally.
        """
        super(GedcomWriterOptionBox, self).parse_options()
        if self.include_witnesses_check:
            self.include_witnesses = self.include_witnesses_check.get_active()
        if self.include_media_check:
            self.include_media = self.include_media_check.get_active()
        if self.include_depot_check:
            self.include_depot = self.include_depot_check.get_active()
        if self.geneanet_obsc_check:
            self.geneanet_obsc = self.geneanet_obsc_check.get_active()
        if self.relativepath_check:
            self.relativepath = self.relativepath_check.get_active()
#        if self.include_persurl:
#            self.include_persurl = self.include_persurl_check.get_active()

    def write_gedcom_file(self, filename):
        """
        Write the actual GEDCOM file to the specified filename.
        """

        self.dirname = os.path.dirname (filename)
        self.gedcom_file = io.open(filename, "w", encoding='utf-8')
        zipf = filename + ".zip"
        self.zipfile = zipfile.ZipFile(zipf,'w')
        if not self.zipfile:
            raise Exception('fichier zip %s non ouvert' % zipf)
        
        LOG.debug("deb write gedcom %d" % self.relativepath)
        self._header(filename)
        self._submitter()
        self._individuals()
        self._families()
        self._sources()
        self._repos()
        self._notes()

        self._writeln(0, "TRLR")
        self._writeln(0, self.relativepath)
        self._writeln(0, self.geneanet_obsc)
        self._writeln(0, self.include_witnesses)
        self.gedcom_file.close()
        self.zipfile.close()
        return True


def export_data(database, filename, user, option_box=None):
    """
    External interface used to register with the plugin system.
    """
    ret = False
    try:
        ged_write = GedcomWriterforGeneanet(database, user, option_box)
#pylint: disable=maybe-no-member
        ret = ged_write.write_gedcom_file(filename)
    except IOError as msg:
        msg2 = _("Could not create %s") % filename
        user.notify_error(msg2, msg)
    except DatabaseError as msg:
        user.notify_db_error(_("Export failed"), msg)
    return ret
