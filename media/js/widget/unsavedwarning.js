// Amara, universalsubtitles.org
//
// Copyright (C) 2012 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('unisubs.UnsavedWarning');

/**
 * @constructor
 * @param {function(boolean)} callback Called with true 
 *     to submit subs, false otherwise.
 */
unisubs.UnsavedWarning = function(callback) {
    goog.ui.Dialog.call(this, null, true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.callback_ = callback;
    this.submitChosen_ = false;
};
goog.inherits(unisubs.UnsavedWarning, goog.ui.Dialog);

unisubs.UnsavedWarning.prototype.createDom = function() {
    unisubs.UnsavedWarning.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var e = this.getElement();
    e.className = 'unisubs-warning';

    var discardLinkText, submitLinkText, warningTitle, warningDescription, cancelLinkText;
    if (unisubs.mode === 'review' || unisubs.mode === 'approve') {
        discardLinkText = 'Discard changes and exit';
        submitLinkText = '';
        warningTitle = 'Really exit?';
        warningDescription = 'If you exit now, your notes will be discarded and all changes will be lost.';
    } else {
        discardLinkText = 'Discard';
        submitLinkText = 'Submit subtitles';
        warningTitle = 'Submit subtitles?';
        warningDescription = 'Do you want to save your work for others to build on? If you were messing around or testing, please discard.';
    }

    cancelLinkText = 'Cancel';

    e.appendChild($d('h2', null, warningTitle));
    e.appendChild($d('p', null, warningDescription));
    this.discardLink_ = $d('a', {'className': 'unisubs-link', 'href':'#'}, discardLinkText);
    this.submitLink_ = $d('a', {'className': 'unisubs-link', 'href': '#'}, submitLinkText);
    this.cancelLink_ = $d('a', {'className': 'unisubs-link', 'href': '#'}, cancelLinkText);
    e.appendChild($d('div', 'unisubs-buttons', this.cancelLink_, this.discardLink_, this.submitLink_));
};
unisubs.UnsavedWarning.prototype.enterDocument = function() {
    unisubs.UnsavedWarning.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(this.cancelLink_, 'click', this.linkClicked_).
        listen(this.discardLink_, 'click', this.linkClicked_).
        listen(this.submitLink_, 'click', this.linkClicked_);
};
unisubs.UnsavedWarning.prototype.linkClicked_ = function(e) {
    e.preventDefault();
    this.submitChosen_ = e.target == this.submitLink_;
    this.cancelChosen_ = e.target == this.cancelLink_;
    this.setVisible(false);
};
unisubs.UnsavedWarning.prototype.setVisible = function(visible) {
    if (this.cancelChosen_) {
        unisubs.UnsavedWarning.superClass_.setVisible.call(this, visible);
        return false;
    }
    if (!visible)
        this.callback_(this.submitChosen_);
    unisubs.UnsavedWarning.superClass_.setVisible.call(this, visible);
};
