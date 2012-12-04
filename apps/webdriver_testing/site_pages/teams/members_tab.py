#!/usr/bin/env python
import time
from ..a_team_page import ATeamPage


class MembersTab(ATeamPage):

    _URL = "teams/%s/members/"
    _USERNAME = "ul.members.listing li h3 a"
    _USER_LANGS = "ul.members.listing li h3 span.descriptor"
    _ROLE = "ul.members.listing li p"
    _ACTIONS = "ul.members.listing li ul.actions li"
    _INVITE_MEMBERS = "div.tools a.button[href*='members/invite']"
    _EDIT_USER = "a.edit-role"
    _SORT_FILTER = "a#sort-filter"

    #EDIT USER MODAL
    _ROLE_PULLDOWN = "select#roles"
    _ROLE_LANG_PULLDOWN = "div#language-restriction select.chzn-select"
    _ROLE_PROJ_PULLDOWN = "div#project-restriction select.chzn-select"
    _SAVE_EDITS = "a.action-save"
    _CANCEL_EDITS = ".modal-footer .action-close"

    #INVITATION FORM (NEARLY IMPOSSIBLE TO DEAL With USERNAME via UI
    _INVITEE_USERNAME_PULLDOWN = "div.ajaxChosen"
    _INVITEE_USERNAME = 'select[name="user_id"]'
    _INVITEE_MESSAGE = "textarea#id_message"
    _INVITEE_ROLE = "select#id_role"
    _INVITATION_SEND = "div.submit button"

    def open_members_page(self, team):
        """Open the team with the provided team slug.

        """
        self.open_page(self._URL % team)
        self.wait_for_element_present(self._SORT_FILTER)


    def user_link(self):
        """Return the url of the first user on the page.

        """
        return self.get_element_attribute(self._USERNAME, 'href')

    def user_languages(self):
        """Return the languages of the first user on the page.

        """
        language_list = []
        els = self.browser.find_elements_by_css_selector(self._USER_LANGS)
        for el in els:
            language_list.append(el.text)
        return language_list

    def user_role(self):
        """Return the of the user role of teh first user on the page.

        """
        return self.get_text_by_css(self._ROLE)

    def invite_user_via_form(self, username, message, role):
        """Invite a user to a team via the invite form.

        """
        
        self.click_by_css(self._INVITE_MEMBERS)
        self.wait_for_element_present(self._INVITEE_USERNAME_PULLDOWN)
        self.click_by_css(self._INVITEE_USERNAME_PULLDOWN)
        self.type_by_css('div.chzn-search input', username)
        if len(username.split()) == 1:
            username = " ".join([username, '('+username+')'])
        self.select_from_chosen(self._INVITEE_USERNAME, 
                                [username])
        self.type_by_css(self._INVITEE_MESSAGE, message)
        self.select_option_by_text(self._INVITEE_ROLE, role)
        self.click_by_css(self._INVITATION_SEND)


    def member_search(self, team_slug, query):
        team_url = self._URL % team_slug
        search_url = "%s?q=%s" % (team_url, query)
        self.open_page(search_url)

    def lang_search(self, team_slug, lang):
        """Open the url of language search term.

        """
        team_url = self._URL % team_slug
        search_url = "%s?lang=%s" % (team_url, lang)
        self.open_page(search_url)

    def edit_user(self, role=None, languages=[], projects=[]):
        """Edit a users roles via the  form.

        """
        self.hover_by_css(self._ROLE)
        self.click_by_css(self._EDIT_USER)
        time.sleep(2)
        if role:
            self.select_option_by_text(self._ROLE_PULLDOWN, role)
        if not languages == []:
            self._language_restrictions(languages)
        if not projects == []:
            self._project_restrictions(projects)
        self.click_by_css(self._SAVE_EDITS)
        time.sleep(2)

    def _language_restrictions(self, languages):
        """Restrict languages via the edit user form.

        """
        self.select_from_chosen(self._ROLE_LANG_PULLDOWN, languages)

    def _project_restrictions(self, projects):
        """Restrict projects via the edit user form.

        """
        self.select_from_chosen(self._ROLE_PROJ_PULLDOWN, projects)
