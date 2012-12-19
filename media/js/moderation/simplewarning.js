
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

goog.require("goog.ui.Dialog");
goog.provide('unisubs.SimpleWarning');

/***
* This is an wrapper for the simplest modeal alert possible. Title, text and OK and Cancel buttons. Shows up when instantiated, it's a
* @constructor
* @param Title 
* @param Main html text
* @param buttons Button set
*/
unisubs.SimpleWarning = function(title, content, okBtLabel,  confirmCallback, cancelBtLabel, opt_cancelCallback) {
    goog.ui.Dialog.call(this, 'unisubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this._content = content;
    this._title = title;
    this._okBtLabel = okBtLabel;
    this._cancelBtLabel = cancelBtLabel;
    this.confirmCallback_ = confirmCallback;
    this.cancelCallback_ = opt_cancelCallback;
    this.setModal(true);

};
goog.inherits(unisubs.SimpleWarning, goog.ui.Dialog);

unisubs.SimpleWarning.prototype.createDom = function() {
    unisubs.SimpleWarning.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var text =  "<h3" + this.title_ + "</h3>" + 
        this._content ;
    this.okLink_ = $d('a', {'className':'unisubs-link unisubs-green-button', 'href':'#'}, this._okBtLabel);
    if (this._cancelBtLabel){
        this.cancelLink_ = $d('a', {'className':'unisubs-link unisubs-green-button', 'href':'#'}, this._cancelBtLabel);
    }else{
        this.cancelLink_  = {};
    }
    this.getElement().className = 'unisubs-warning';
    var label = $d('div', 'unisubs-label');
    label.innerHTML = text;
    this.getElement().appendChild(label);
    this.getElement().appendChild($d('div', 'unisubs-buttons', this.okLink_));
    if (this._cancelBtLabel){
        this.getElement().appendChild($d('div', 'unisubs-buttons', this.cancelLink_));
    }
    
                                     
};

unisubs.SimpleWarning.prototype.enterDocument = function() {
    unisubs.SimpleWarning.superClass_.enterDocument.call(this);
    var that = this;
    this.getHandler().listenOnce(
        this.okLink_, 'click', 
        function(e) {
            e.preventDefault();
            that.setVisible(false);
            this.confirmCallback_();
        }).listenOnce(
        this.cancelLink_, 'click', 
        function(e) {
            e.preventDefault();
            that.setVisible(false);
            if (this.cancelCallback_){
                this.cancelCallback_()
            }
        });;
};
