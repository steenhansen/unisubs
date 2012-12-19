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

goog.provide('unisubs.subtitle.SubtitleWidget');

/**
 * @constructor
 * @extends goog.ui.Component
 *
 * @param {unisubs.subtitle.EditableCaption} subtitle
 * @param {unisubs.subtitle.EditableCaptionSet} subtitleSet
 *
 *
 */
unisubs.subtitle.SubtitleWidget = function(subtitle,
                                           subtitleSet,
                                           editingFn,
                                           displayTimes,
                                           readOnly,
                                           displayParagraphMarker) {
    goog.ui.Component.call(this);
    this.originalNode_ = subtitle;
    this.subtitleSet_ = subtitleSet;
    this.editingFn_ = editingFn;
    this.displayTimes_ = displayTimes;
    this.keyHandler_ = null;
    this.timeSpinner_ = null;
    this.readOnly_ = readOnly;
    this.displayParagraphMarker_ = displayParagraphMarker;
    this.insertDeleteButtonsShowing_ = false;
};
goog.inherits(unisubs.subtitle.SubtitleWidget, goog.ui.Component);

unisubs.subtitle.SubtitleWidget.prototype.getContentElement = function() {
    return this.contentElement_;
};
unisubs.subtitle.SubtitleWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    if (!this.readOnly_) {
        this.deleteButton_ = this.createDeleteButton_($d);
        this.insertButton_ = this.createInsertButton_($d);
        this.paragraphMarkerButton_ = this.createParagraphMarkerButton_($d);
        this.updateParagraphMarkerButton_();
        goog.style.showElement(this.deleteButton_, false);
        goog.style.showElement(this.insertButton_, false);
        goog.style.showElement(this.paragraphMarkerButton_, false);
        this.contentElement_ = $d('span', 'unisubs-timestamp');

        this.setElementInternal(
            $d('li', null,
            this.contentElement_,
            this.titleElem_ =
            $d('span', {'className':'unisubs-title' + (this.subtitleSet_.languageIsRTL ? ' is-rtl' : '')},
                this.titleElemInner_ =
                $d('span')),
            this.deleteButton_,
            this.insertButton_, 
            this.paragraphMarkerButton_
        ));
        
    } else {
        this.setElementInternal(
            $d('li', null,
            this.contentElement_,
            this.titleElem_ =
            $d('span', {'className':'unisubs-title'},
                this.titleElemInner_ =
                $d('span'))));
        this.contentElement_ = $d('span', 'unisubs-timestamp');
    }
    if (!this.displayTimes_) {
        goog.dom.classes.add(this.titleElem_, 'unisubs-title-notime');
        unisubs.style.showElement(this.contentElement_, false);
        var startTime = this.subtitleSet_.x['startTime'](this.originalNode_.node);
        if (parseFloat(startTime) > -1) {
            var timeElement = $d('span', {'className': 'unisubs-timestamp-time-fixed'}, 
                                unisubs.formatTime(startTime));
            this.titleElem_.appendChild(timeElement);
        }
    }
    else {
        this.timeSpinner_ = new unisubs.Spinner(
            this.originalNode_.getStartTime(),
            goog.bind(this.originalNode_.getMinStartTime, this.originalNode_),
            goog.bind(this.originalNode_.getMaxStartTime, this.originalNode_),
            unisubs.formatTime);
        this.addChild(this.timeSpinner_, true);
    }
    this.textareaElem_ = null;
    this.keyHandler_ = null;
    this.docClickListener_ = null;
    this.updateValues_();
    this.showingTextarea_ = false;
    this.editing_ = false;
};
unisubs.subtitle.SubtitleWidget.prototype.createDeleteButton_ = function($d) {
    return $d('div', 'unisubs-sub-delete', ' ');
};
unisubs.subtitle.SubtitleWidget.prototype.createParagraphMarkerButton_ = function($d) {
    return $d('div', 'unisubs-sub-paragraph', ' ');
    
};
unisubs.subtitle.SubtitleWidget.prototype.createInsertButton_ = function($d) {
    return $d('div', 'unisubs-sub-insert', ' ');
};
unisubs.subtitle.SubtitleWidget.prototype.enterDocument = function() {
    unisubs.subtitle.SubtitleWidget.superClass_.enterDocument.call(this);
    var et = goog.events.EventType;

    if (!this.readOnly_) {
        this.getHandler().listen(this.deleteButton_, et.CLICK, this.deleteClicked_)
                         .listen(this.insertButton_, et.CLICK, this.insertClicked_)
                         .listen(this.paragraphMarkerButton_, et.CLICK, this.paragraphMarkerClicked_)
                         .listen(this.titleElem_, et.CLICK, this.clicked_)
                         .listen(this.getElement(),
                                [et.MOUSEOVER, et.MOUSEOUT],
                                this.mouseOverOut_)
                         .listen(this.originalNode_,
                                 unisubs.subtitle.EditableCaption.CHANGE,
                                 this.updateValues_);
    }

    if (this.timeSpinner_)
        this.getHandler().listen(
            this.timeSpinner_,
            goog.object.getValues(unisubs.Spinner.EventType),
            this.timeSpinnerListener_);
};
unisubs.subtitle.SubtitleWidget.prototype.setActive = function(active) {
    goog.dom.classes.enable(this.getElement(), 'active', active);
};
unisubs.subtitle.SubtitleWidget.prototype.deleteClicked_ = function(e) {
    this.subtitleSet_.deleteCaption(this.originalNode_);
};

unisubs.subtitle.SubtitleWidget.prototype.updateParagraphMarkerButton_ = function() {
    if (this.subtitleSet_.x['startOfParagraph'](this.originalNode_.node)){
        goog.dom.classes.add(this.paragraphMarkerButton_, "selected")
    }else{
        
        goog.dom.classes.remove(this.paragraphMarkerButton_, "selected")
    }

}
unisubs.subtitle.SubtitleWidget.prototype.paragraphMarkerClicked_ = function(e) {
    e.stopPropagation();
    this.originalNode_.toggleStartOfParagraph();
    this.updateParagraphMarkerButton_();
};

unisubs.subtitle.SubtitleWidget.prototype.insertClicked_ = function(e) {
    e.stopPropagation();
    this.showInsertDeleteButtons_(false);
    this.subtitleSet_.insertCaption(this.originalNode_.getSubOrder());
};
unisubs.subtitle.SubtitleWidget.prototype.timeSpinnerListener_ =
    function(event)
{
    var et = unisubs.Spinner.EventType;
    if (event.type == et.ARROW_PRESSED)
        this.setEditing_(true, true);
    else if (event.type == et.VALUE_CHANGED) {
        this.originalNode_.setStartTime(event.value);
        this.setEditing_(false, true);
    }
};
unisubs.subtitle.SubtitleWidget.prototype.setEditing_ = function(editing, timeChanged) {
    this.editingFn_(editing, timeChanged, this);
    this.editing_ = editing;
    if (!editing)
        this.updateValues_();
};
/**
 *
 * @return {mirosub.subtitle.EditableCaption} The subtitle for this widget.
 */
unisubs.subtitle.SubtitleWidget.prototype.getSubtitle = function() {
    return this.originalNode_;
};
unisubs.subtitle.SubtitleWidget.prototype.mouseOverOut_ = function(e) {
    if (e.type == goog.events.EventType.MOUSEOVER &&
        !unisubs.subtitle.SubtitleWidget.editing_)
        this.showInsertDeleteButtons_(true);
    else if (e.type == goog.events.EventType.MOUSEOUT)
        this.showInsertDeleteButtons_(false);
};
unisubs.subtitle.SubtitleWidget.prototype.showInsertDeleteButtons_ =
    function(show)
{
    if (show == this.insertDeleteButtonsShowing_)
        return;
    this.insertDeleteButtonsShowing_ = show;

    if (!this.readOnly_) {
        goog.style.showElement(this.deleteButton_, show);
        goog.style.showElement(this.insertButton_, show);
        goog.style.showElement(this.paragraphMarkerButton_, show);
    }
};
unisubs.subtitle.SubtitleWidget.prototype.clicked_ = function(event) {
    if (this.showingTextarea_)
        return;
    if (unisubs.subtitle.SubtitleWidget.editing_) {
        unisubs.subtitle.SubtitleWidget.editing_.switchToView_();
        return;
    }
    this.switchToEditMode();
    event.stopPropagation();
    event.preventDefault();
};
unisubs.subtitle.SubtitleWidget.prototype.switchToEditMode = function() {
    this.showInsertDeleteButtons_(false);
    unisubs.subtitle.SubtitleWidget.editing_ = this;
    this.setEditing_(true, false);
    this.showingTextarea_ = true;
    this.docClickListener_ = new goog.events.EventHandler();
    var that = this;
    this.docClickListener_.listen(
        document, goog.events.EventType.CLICK,
        function(event) {
            if (event.target != that.textareaElem_) {
                that.switchToView_();
            }
        });
    goog.dom.removeNode(this.titleElemInner_);
    this.textareaElem_ = this.getDomHelper().createDom(
        'textarea', 'unisubs-subedit');
    goog.dom.append(this.titleElem_, this.textareaElem_);
    this.textareaElem_.value = this.originalNode_.getText();
    this.textareaElem_.focus();
    this.keyHandler_ = new goog.events.KeyHandler(this.textareaElem_);
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_, false, this);

};
unisubs.subtitle.SubtitleWidget.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER && !event.shiftKey) {
        this.switchToView_();
        event.stopPropagation();
        event.preventDefault();
    }
};
unisubs.subtitle.SubtitleWidget.prototype.switchToView_ = function() {
    if (!this.showingTextarea_)
        return;
    unisubs.subtitle.SubtitleWidget.editing_ = null;
    this.getHandler().unlisten(this.keyHandler_);
    this.disposeEventHandlers_();
    this.originalNode_.setText(this.textareaElem_.value);
    goog.dom.removeNode(this.textareaElem_);
    this.titleElem_.appendChild(this.titleElemInner_);
    this.showingTextarea_ = false;
    this.setEditing_(false, false);
};
unisubs.subtitle.SubtitleWidget.prototype.clearTimes = function() {
    unisubs.style.setVisibility(this.contentElement_, false);
};
unisubs.subtitle.SubtitleWidget.prototype.updateValues_ = function() {
    if (this.editing_)
        return;
    if (this.displayTimes_) {
        var time = this.subtitleSet_.x['startTime'](this.originalNode_.node);
        this.contentElement_.style.visibility =
            time == -1 ? 'hidden' : 'visible';
        if (time != -1)
            this.timeSpinner_.setValue(time);
    }
    // FIXME: Sanitize / wrap to the right elements (<em>... etc)
    this.titleElemInner_.innerHTML = goog.string.newLineToBr(
        this.subtitleSet_.x['contentRendered'](
            this.originalNode_.node
        )
    );

};
unisubs.subtitle.SubtitleWidget.prototype.disposeEventHandlers_ = function() {
    if (this.keyHandler_) {
        this.keyHandler_.dispose();
        this.keyHandler_ = null;
    }
    if (this.docClickListener_) {
        this.docClickListener_.dispose();
        this.docClickListener_ = null;
    }
};
unisubs.subtitle.SubtitleWidget.prototype.disposeInternal = function() {
    unisubs.subtitle.SubtitleWidget.superClass_.disposeInternal.call(this);
    this.disposeEventHandlers_();
};
