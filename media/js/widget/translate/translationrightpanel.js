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

goog.provide('unisubs.translate.TranslationRightPanel');
/**
* @constructor
* @extends unisubs.RightPanel
*/

unisubs.translate.TranslationRightPanel = function(dialog,
                                                    serverModel,
                                                    helpContents,
                                                    extraHelp,
                                                    legendKeySpecs,
                                                    showRestart,
                                                    doneStrongText,
                                                    doneText,
                                                    extraHelpHeader,
                                                    isReviewOrApproval ) {
    unisubs.RightPanel.call(this, serverModel, helpContents, extraHelp,
                             legendKeySpecs,
                             showRestart, doneStrongText, doneText);
    this.extraHelpHeader_ = extraHelpHeader;
    this.dialog_ = dialog;
    this.isReviewOrApproval_ = isReviewOrApproval;
    this.showSaveExit = true;
};
goog.inherits(unisubs.translate.TranslationRightPanel, unisubs.RightPanel);

unisubs.translate.TranslationRightPanel.prototype.appendExtraHelpInternal =
    function($d, el)
{
    if (this.isReviewOrApproval_){
        return;
    }
    var extraDiv = $d('div', 'unisubs-extra unisubs-translationResources');
    extraDiv.appendChild($d('h3', {'className': 'unisubs-resources'}, this.extraHelpHeader_));

    var lst = $d('ul', {'className': 'unisubs-resourceList'});
    for (var i = 0; i < this.extraHelp_.length; i++) {
        var linkText = this.extraHelp_[i][0];
        var linkHref = this.extraHelp_[i][1];
        lst.appendChild($d('li', {'className': 'unisubs-resource'},
                           $d('a', {'target':'_blank', 'href': linkHref,
                                    'className': 'unisubs-resourceLink' },
                              linkText)));
    }
    extraDiv.appendChild(lst);
    el.appendChild(extraDiv);
    this.autoTranslateLink_ = 
        $d('a', {'href':'#'}, 'Auto-translate empty fields');
    this.changeTimingLink_ =
        $d('a', {'href':'#'}, 'Convert to Timed Subtitles');

    var isBingTranslateable = unisubs.translate.BingTranslator.isTranslateable(
        this.dialog_.getStandardLanguage(),
        this.dialog_.getSubtitleLanguage());

    var ul =  $d('ul', 'unisubs-translationOptions');
    
    if (isBingTranslateable) {
        ul.appendChild($d('li', 'unisubs-autoTranslate', this.autoTranslateLink_, 
            $d('span', null, ' (using bing)')));
    }

    if (unisubs.timing_mode == 'on') {
        ul.appendChild(
            $d('li', 'unisubs-changeTiming',
               this.changeTimingLink_,
               $d('span', null, ' (advanced)')));
    }
    el.appendChild(ul);
};

unisubs.translate.TranslationRightPanel.prototype.appendMiddleContentsInternal = function($d, el) {

}

unisubs.translate.TranslationRightPanel.prototype.enterDocument = function() {
    unisubs.translate.TranslationRightPanel.superClass_.enterDocument.call(this);
    
    var handler = this.getHandler();
    if (this.changeTimingLink_){
        // when reviewing / approving this link will not be present
        handler.listen(
        this.changeTimingLink_,
        'click',
        this.changeTimingClicked_);
    }
   
    if (this.autoTranslateLink_){
        // when reviewing / approving this link will not be present
        handler.listen(this.autoTranslateLink_, 'click', this.autoTranslateClicked_)
    }
};

unisubs.translate.TranslationRightPanel.prototype.autoTranslateClicked_ = function(e){
    e.preventDefault();
    this.dialog_.translateViaBing();
}

unisubs.translate.TranslationRightPanel.prototype.changeTimingClicked_ = 
    function(e) 
{
    e.preventDefault();
    this.dialog_.forkAndClose();
};