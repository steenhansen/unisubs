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

goog.provide('unisubs.startdialog.Model');

/**
 * @constructor
 * @param {Object} json from widget rpc
 * @param {unisubs.widget.SubtitleState=} opt_langState The subtitle state to display initially.
 */
unisubs.startdialog.Model = function(json, opt_langState) {
    /**
     * @type {Array.<string>} Array of langauge codes
     */
    this.myLanguages_ = json['my_languages'];
    this.limitLanguages_ = json['limit_languages'];
    this.blockedLanguages_ = json['blocked_languages'];
    goog.array.removeDuplicates(this.myLanguages_);
    this.myLanguages_ = goog.array.filter(
        this.myLanguages_, function(l) {
            return !!unisubs.languageNameForCode(l);
        });
    this.originalLanguage_ = json['original_language'];
    this.videoLanguages_ = new unisubs.startdialog.VideoLanguages(
        json['video_languages']);
    this.toLanguages_ = new unisubs.startdialog.ToLanguages(
        this.myLanguages_, this.videoLanguages_, this.limitLanguages_,
        opt_langState);
    /**
     * @type {?string}
     */
    this.selectedOriginalLanguage_ = null;
    if (opt_langState){
        // with a pk we can know for sure that we need one english in particular
        // (if there are +1 with the same lang code)
        if (opt_langState.LANGUAGE_PK){
            this.selectedLanguage_ = this.toLanguages_.forKey(
                opt_langState.LANGUAGE+opt_langState.LANGUAGE_PK);
        } else {
            this.selectedLanguage_ = this.toLanguages_.forLangCode(
                opt_langState.LANGUAGE);
        }

    }
};

unisubs.startdialog.Model.prototype.getOriginalLanguage = function() {
    return this.originalLanguage_;
};

unisubs.startdialog.Model.prototype.originalLanguageShown = function() {
    return !this.originalLanguage_;
};

/**
 * @returns {Array.<unisubs.startdialog.ToLanguage>}
 */
unisubs.startdialog.Model.prototype.toLanguages = function() {
    return this.toLanguages_.getToLanguages();
};

/**
 * @returns {unisubs.startdialog.ToLanguage}
 */
unisubs.startdialog.Model.prototype.getSelectedLanguage = function() {
    if (!this.selectedLanguage_)
        this.selectedLanguage_ = this.toLanguages_.getToLanguages()[0];
    return this.selectedLanguage_;
};

/**
 * @param {string} key KEY from toLanguages to select
 */
unisubs.startdialog.Model.prototype.selectLanguage = function(key) {
    this.selectedLanguage_ = this.toLanguages_.forKey(key);
};

/**
 * @param {string} language language code to select.
 */
unisubs.startdialog.Model.prototype.selectOriginalLanguage = function(language) {
    this.selectedOriginalLanguage_ = language;
};

unisubs.startdialog.Model.prototype.findFromForPK = function(pk) {
    return this.videoLanguages_.findForPK(pk);
};

unisubs.startdialog.Model.prototype.bestLanguages = function(toLangCode, fromLangCode) {
    var videoLanguage = this.videoLanguages_.findForLanguagePair(
        toLangCode, fromLangCode);
    if (!videoLanguage)
        return null;
    return [this.toLanguages_.forVideoLanguage(videoLanguage),
            videoLanguage.getStandardLang()];
};

/**
 * @return {Array.<unisubs.startdialog.LanguageSummary>}
 */
unisubs.startdialog.Model.prototype.fromLanguages = function() {
    var originalLanguage = this.originalLanguage_;
    if (!originalLanguage)
        originalLanguage = this.selectedOriginalLanguage_;
    var selectedLanguage = this.getSelectedLanguage();
    if (selectedLanguage.LANGUAGE == originalLanguage)
        return [];
    var videoLanguages = this.videoLanguages_.findForLanguage(
        selectedLanguage.LANGUAGE);
    var possibleFromLanguages = [];
    this.videoLanguages_.forEach(function(vl) {
        if (!goog.array.contains(videoLanguages, vl))
            possibleFromLanguages.push(vl);
    });
    possibleFromLanguages = goog.array.filter(
        possibleFromLanguages,
        function(vl) {
            return (vl.DEPENDENT && vl.PERCENT_DONE > 0) ||
                (!vl.DEPENDENT && vl.SUBTITLE_COUNT > 0);
        });
    var myLanguages = new goog.structs.Set(this.myLanguages_);
    goog.array.sort(
        possibleFromLanguages,
        function(a, b) {
            return goog.array.defaultCompare(
                myLanguages.contains(a.LANGUAGE) ? 0 : 1,
                myLanguages.contains(b.LANGUAGE) ? 0 : 1);
        });
    return possibleFromLanguages;
};

unisubs.startdialog.Model.prototype.toLanguageForKey = function(key) {
    return this.toLanguages_.forKey(key);
};
