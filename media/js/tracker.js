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

goog.provide('unisubs.Tracker');

/**
 * @constructor
 */
unisubs.Tracker = function() {
    this.accountSet_ = false;
};

goog.addSingletonGetter(unisubs.Tracker);

unisubs.Tracker.prototype.ACCOUNT_ = 'UA-163840-22';
unisubs.Tracker.prototype.PREFIX_ = 'usubs';

unisubs.Tracker.prototype.gaq_ = function() {
    return window['_gaq'];
};

unisubs.Tracker.prototype.trackEvent = function(category, action, opt_label, opt_value) {
    if (unisubs.REPORT_ANALYTICS) {
        this.setAccount_();
        this.gaq_().push(
            [this.PREFIX_ + "._trackEvent", category, action, opt_label, opt_value]);
    }
};

unisubs.Tracker.prototype.trackPageview = function(pageview, opt_props) {
    if (unisubs.REPORT_ANALYTICS) {
        var props = opt_props || {};
        props['onsite'] = unisubs.isFromDifferentDomain() ? 'no' : 'yes';
        this.setAccount_();
        this.gaq_().push([this.PREFIX_ + '._trackPageview', '/widget/' + pageview]);
    }
};

unisubs.Tracker.prototype.setAccount_ = function() {
    if (!this.accountSet_) {
        window['_gaq'] = this.gaq_() || [];
        this.loadGA_();
        this.gaq_().push([this.PREFIX_ + '._setAccount', this.ACCOUNT_]);
        this.accountSet_ = true;
    }
};

unisubs.Tracker.prototype.loadGA_ = function() {
    if (unisubs.REPORT_ANALYTICS) {
        var url = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        unisubs.addScript(url, true);
    }
};
