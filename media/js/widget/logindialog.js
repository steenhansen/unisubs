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

goog.provide('unisubs.LoginDialog');

/**
 * @constructor 
 * @param {function(boolean)=} Called when login process completes.
 *     Passed true if logged in successfully, false otherwise.
 * @param {String} Optional message to show at the top of the login dialog.
 */
unisubs.LoginDialog = function(opt_finishFn, opt_message) {
    goog.ui.Dialog.call(this, 'unisubs-modal-login', true);
    this.setBackgroundElementOpacity(0);
    this.finishFn_ = opt_finishFn;
    this.message_ = opt_message;
    this.loggedIn_ = !!unisubs.currentUsername;
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.imageLoader_ = new goog.net.ImageLoader();
    this.bigSpinnerGifURL_ = unisubs.imageAssetURL('big_spinner.gif');
    this.imageLoader_.addImage('bigSpinner', this.bigSpinnerGifURL_);
    this.imageLoader_.start();
};
goog.inherits(unisubs.LoginDialog, goog.ui.Dialog);
/**
 * The currently-opened login dialog.
 */
unisubs.LoginDialog.currentDialog_ = null;

unisubs.LoginDialog.prototype.createDom = function() {
    unisubs.LoginDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.loginLink_ = 
        $d('a', {'className': 'unisubs-log', 'href': '#'},
           $d('span', null, 'Log in or Create an Account'));
    this.twitterLink_ = 
        $d('a', {'className': 'unisubs-twitter', 'href': '#'},
           $d('span', null, 'Twitter'));
    this.openidLink_ =
        $d('a', {'className': 'unisubs-openid', 'href': '#'},
           $d('span', null, 'OpenID'));
    this.googleLink_ =
        $d('a', {'className': 'unisubs-google', 'href': '#'},
           $d('span', null, 'Google'));
    this.facebookLink_ =
        $d('a', {'className': 'unisubs-facebook', 'href': '#'},
           $d('span', null, 'Facebook'));
    var el = this.getContentElement();
    if (this.message_)
        goog.dom.appendChild(el,
            $d('h4', {'className': 'unisubs-login-message'},
               this.message_));
    // FIXME: update these to use goog.dom.append as soon as we upgrade
    // to new version of closure.
    goog.dom.appendChild(
        el, $d('h4', null, 'Login using any of these options'));
    goog.dom.appendChild(el, this.loginLink_);
    goog.dom.appendChild(el, this.twitterLink_);
    goog.dom.appendChild(el, this.openidLink_);
    goog.dom.appendChild(el, this.googleLink_);
    goog.dom.appendChild(el, this.facebookLink_);
    goog.dom.appendChild(
        el, 
        $d('p', 'unisubs-small', 
           'For security, the login prompt will open in a separate window.'));
};

unisubs.LoginDialog.prototype.showLoading_ = function() {
    goog.dom.removeChildren(this.getContentElement());
    this.getElement().appendChild(
        this.getDomHelper().createDom(
            'img', {
                'className': 'big_spinner', 
                'src': this.bigSpinnerGifURL_
            }));
};

unisubs.LoginDialog.prototype.enterDocument = function() {
    unisubs.LoginDialog.superClass_.enterDocument.call(this);
    var that = this;
    this.getHandler().
        // for some reason, event.target doesn't get transmitted 
        // for this.loginLink_
        listen(this.loginLink_, 'click', this.siteLoginClicked_).
        listen(this.twitterLink_, 'click', this.clicked_).
        listen(this.openidLink_, 'click', this.clicked_).
        listen(this.googleLink_, 'click', this.clicked_).
        listen(this.facebookLink_, 'click', this.clicked_);
};

unisubs.LoginDialog.prototype.siteLoginClicked_ = function(e) {
    this.showLoading_();
    this.loginWin_ = unisubs.openLoginPopup(
        unisubs.LoginPopupType.NATIVE,
        goog.bind(this.processCompleted_, this),
        goog.bind(this.loginSiteError_, this));
    e.preventDefault();
};

unisubs.LoginDialog.prototype.clicked_ = function(e) {
    this.showLoading_();
    var type;
    if (e.target == this.loginLink_)
        type = unisubs.LoginPopupType.NATIVE;
    else if (e.target == this.twitterLink_)
        type = unisubs.LoginPopupType.TWITTER;
    else if (e.target == this.openidLink_)
        type = unisubs.LoginPopupType.OPENID;
    else if (e.target == this.googleLink_)
        type = unisubs.LoginPopupType.GOOGLE;
    else
        type = unisubs.LoginPopupType.FACEBOOK;
    this.loginWin_ = unisubs.openLoginPopup(
        type, 
        goog.bind(this.processCompleted_, this),
        goog.bind(this.loginSiteError_, this));
    e.preventDefault();
};

unisubs.LoginDialog.prototype.loginSiteError_ = function(status) {
    alert('We had a problem logging you in to the site. Most likely your ' +
          'network connection is flaky, or there is a serious problem ' +
          'with our server. You might want to try again.\n\nIf you are ' +
          'subtitling a video, you can always use the download subtitles link ' +
          'in the lower right corner of the dialog.');
};

unisubs.LoginDialog.prototype.processCompleted_ = function(loggedIn) {
    this.loginWin_ = null;
    this.loggedIn_ = loggedIn;
    this.setVisible(false);
};

unisubs.LoginDialog.prototype.setVisible = function(visible) {
    unisubs.LoginDialog.superClass_.setVisible.call(this, visible);
    unisubs.LoginDialog.currentDialog_ = visible ? this : null;
    if (!visible) {
        if (goog.isDefAndNotNull(this.loginWin_) && !this.loginWin_['closed']) {
            try {
                this.loginWin_['close']();
            }
            catch (e) {
                // do nothing
            }
        }
    }
    if (!visible && this.finishFn_)
        this.finishFn_(this.loggedIn_);
};

unisubs.LoginDialog.prototype.disposeInternal = function() {
    unisubs.LoginDialog.superClass_.disposeInternal.call(this);
    this.imageLoader_.dispose();
};

unisubs.LoginDialog.isCurrentlyShown = function() {
    return unisubs.LoginDialog.currentDialog_ != null;
};

unisubs.LoginDialog.logout = function() {
    unisubs.Rpc.call('logout', {}, function(result) {
        unisubs.currentUsername = null;
        unisubs.userEventTarget.dispatchEvent(unisubs.EventType.LOGOUT);
    });
};
