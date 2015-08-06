/*
 * This module is for payment processing.
 */

jQuery(function($) {
	'use strict';

	//csrf
	var Csrf = {
		$csrfToken : null,
		init : function() {
			this.$csrfToken = this.getCookie('csrftoken');
			/* setting up ajax */
			$.ajaxSetup({
				beforeSend : function(xhr, settings) {
					if (!(/^http:./.test(settings.url) || /^https:./
							.test(settings.url))) {
						// Only send the token to relative URLs i.e. locally.
						xhr.setRequestHeader("X-CSRFToken", this.$csrfToken);
					}
				}
			});

			return this;
		},
		getToken : function() {
			if (typeof (this.$csrfToken) == 'undefined')
				this.$csrfToken = this.getCookie('csrftoken');
			return this.$csrfToken;
		},
		setHeader : function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", this.$csrfToken);
		},
		getCookie : function(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie
								.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}
	};

	var RechargeApp = {
		$specialKeys : [ 18, 37, 38, 39, 40, 8, 20, 17, 46, 35, 13, 27, 36, 45, 144, 33, 34, 16, 9, 91 ], //special chars/keys

		$rechargeplanSel : $("#rechargeplan"),
		$rechargeplanLbl : $("#recharge_total_pr"),
		$rcLbl : $("#reclbl"),

		$planCredits : [],
		$memberPrices : [],

		$rechargePrices : [],
		$rechargeCreditPlans : [],
		$selMemberTotalPrice : 0,
		$selMemberPrice : 0,
		$selPlanIdx : 0,
		$isUnlimitedPlan: false,

		$commonApp : null,
		init : function(commonapp_ins) {
			//initializing
			this.$specialKeys.push(8); //Backspace
			this.$specialKeys.push(16); //Shift
			this.$specialKeys.push(17); //Ctl
			this.$specialKeys.push(18); //Alt

			this.$rechargePrices = [ 999, 3499, 8599, 49999, 50000 ];
			this.$rechargeCreditPlans = [ 1500, 6000, 18000, 125000 ];

			this.$selRechargePrice = 3499;

			this.$commonApp = commonapp_ins;
			this.bindEvents();

			return this;
		},
		bindEvents : function() {
			this.$rechargeplanSel.on('change', this.changeRechargePrice.bind(this));
			
		},
		getRecCalculatedAmt : function() {
			return this.$selRechargePrice;
		},
		getCurrentSelectedPlanCredit : function() {
			var selPlanIdx = this.$rechargeplanSel.val();
			return this.$rechargeCreditPlans[selPlanIdx];
		},
		
		changeRechargePrice : function(event) {
			this.$selPlanIdx = this.$rechargeplanSel.val();
			this.$selRechargePrice = this.$rechargePrices[this.$selPlanIdx];
			this.$rechargeplanLbl.text(this.$commonApp.getFormattedNo(this.$selRechargePrice));
			this.$rcLbl.show();
			this.$commonApp.changeTotal();
		},
	};

	var GroupApp = {
		$groupRow : $("#groupRow"),
		$grpSize : $("#grpsize"),
		$norGroupLbl : $("#normal-grp"),
		$grpPriceLbl : $("#grp_total_pr"),

		$selGroupPrice : 0,
		$selGrpIdx : 0,
		$oneGroupPrice : 3798,
		$commonApp : null,

		init : function(commonapp_ins) {
			this.setGrpCalculatedDefaultAmt();
			this.$commonApp = commonapp_ins;
			this.bindEvents();

			return this;
		},
		getGrpCalculatedAmt : function() {
			return this.$selGroupPrice;
		},
		setGrpCalculatedDefaultAmt: function() {
			this.$selGroupPrice = this.$oneGroupPrice;
		},
		resetGrpCalculatedDefaultAmt: function() {
			this.$selGroupPrice = 0;
		},
		bindEvents : function() {
			this.$grpSize.on('change', this.changeGroupPrice.bind(this));
		},
		changeGroupPrice : function(e) {
			this.$selGrpIdx = this.$grpSize.val();
			this.$selGroupPrice = this.$oneGroupPrice * this.$selGrpIdx;
			this.$grpPriceLbl.text(this.$commonApp.getFormattedNo(this.$selGroupPrice));
			this.$commonApp.changeTotal();
		},
		getSelectedGroup : function() {
			return this.$grpSize.val();
		},
	};

	var CouponApp = {
		$couponValInp : $("#coupon"),
		$couponErrorLbl : $("#couponErrorLbl"),
		$applyBtn : $("#applyBtn"),
		$urlInput: $("#coupon_url"),

		$commonApp : null,

		init : function(commonapp_ins) {
			this.$commonApp = commonapp_ins;
			this.bindEvents();
			return this;
		},
		bindEvents : function() {
			this.$couponValInp.on('dblclick', this.enableCoupon.bind(this));
			this.$applyBtn.on('click', this.applyCoupon.bind(this));
		},
		enableCoupon : function() {
			this.$applyBtn.button('reset');
			this.$couponValInp.removeAttr('readonly');
			this.$couponValInp.val('');
			this.$couponErrorLbl.html('');
			this.$commonApp.changeTotal();
		},
		showError : function(error) {
			this.$couponErrorLbl.html(error);
			this.$couponErrorLbl.removeClass("label-success-c");
			this.$couponErrorLbl.addClass("label-error");
		},
		applyCoupon : function(event) {
			event.preventDefault();

			this.$applyBtn.button('loading');
			var famt = this.$commonApp.getTotalPriceWithoutTax();

			if (famt < 0) {
				this.$couponErrorLbl.text("Total amount should be greater than 0");
				this.$couponErrorLbl.addClass("label-error");
				this.$applyBtn.button('reset');
			} else if (this.$couponValInp.val() == '' || typeof (this.$couponValInp.val()) == 'undefined') {
				this.$couponValInp.addClass('field-error');
				this.$couponErrorLbl.text("Please enter coupon code");
				this.$couponErrorLbl.addClass("label-error");
				this.$applyBtn.button('reset');
			} else {
				this.$couponValInp.removeClass('field-error');

				var $this = this;
				$.ajax({
					type : "POST",
					withCredentials : true,
					async : false,
					url : $this.$urlInput.val(),
					headers : {
						csrftoken : this.$commonApp.getCSRFToken()
					},
					data : {
						csrfmiddlewaretoken : this.$commonApp.getCSRFToken(),
						code : this.$couponValInp.val(),
						amount : famt
					},
					success : function(json) {
						if (typeof (json.error) != 'undefined' && json.error != '') {
							$this.$couponErrorLbl.html(json.error);
							$this.$couponErrorLbl.removeClass("label-success-c");
							$this.$couponErrorLbl.addClass("label-error");
							$this.$couponValInp.addClass('field-error');
							$this.$commonApp.setNewAmount(json.new_amount);
						} else {
							$this.$couponErrorLbl.html(json.success);
							$this.$couponErrorLbl.removeClass("label-error");
							$this.$couponErrorLbl.addClass("label-success-c");
							$this.$couponValInp.removeClass('field-error');
							$this.$couponValInp.attr('readonly', 'readonly');
							$this.$commonApp.setNewAmount(json.new_amount);
						}
						$this.$applyBtn.button('reset');
						return false;
					},
					error : function(jqxhr, textStatus, errorThrown) {
						console.log(jqxhr);
						console.log(textStatus);
						console.log(errorThrown);
						$this.$applyBtn.button('reset');
					}
				});
				return false;
			}
			return false;
		}
	};

	var CommonApp = {
		$payBtn : $("#btnpay"),
		$secureAmt : $("#id_secure_hash"),
		$amtHidden : $("#id_amount"),
		$totalPriceBtn : $("#total_prbtn"),
		$totalPriceWithoutTax : $("#total_pr_without_tax"),
		$taxPercantage : $("#tax_pr"),
		$refNoHidden : $("#id_reference_no"),
		$form : $("#frmTransaction"),
		$urlInput: $("#hash_url"),
		$choiceCheckboxes : $("input[name=choiceCheckbox]"),
		$buyMessagesRadio: $("#buy_messages"),
		$buyGroupsRadio: $("#buy_groups"),
		$option: null,
		$isGroupEnabled: true,
		$isMessageEnabled: true,
		$csrf : Csrf.init(),
		$couponApp : null,
		$groupApp : null,
		$rechargeApp : null,
		$tax_percantage : [],
		$tax_label : [],
		init : function() {
			//initializing
			this.$couponApp = CouponApp.init(this);
			this.$groupApp = GroupApp.init(this);
			this.$rechargeApp = RechargeApp.init(this);
			this.$option = 3;
			this.bindEvents();
			var taxPercantage = 0;
		},
		bindEvents : function() {
			this.$payBtn.on('click', this.getSecureHash.bind(this));
			this.$choiceCheckboxes.on('change', this.changePurchaseChoice.bind(this));
		},
		changePurchaseChoice: function(e) {
			var target_sec = $($(e.target).attr('target'));
			if($(e.target).is(":checked")) {
				target_sec.fadeIn(500);
			} else {
				target_sec.fadeOut(500);
			}
			
			//resetting selected prices
			this.$isGroupEnabled = this.$buyGroupsRadio.is(":checked");
			this.$isMessageEnabled = this.$buyMessagesRadio.is(":checked");
			
			if(!this.$buyMessagesRadio.is(":checked") && !this.$buyGroupsRadio.is(":checked")) {
				this.$buyMessagesRadio.prop( "checked", true );
				this.$buyMessagesRadio.trigger("change");
				this.$isMessageEnabled = true;
			}
			this.changeTotal();
		},
		getCurrentAmount : function() {
			this.changeTotal();
			return this.$amtHidden.val();
		},
		getSecureHash : function(event) {
			event.preventDefault();
			var credits = 0, groups = 0;
			if(this.$isGroupEnabled && this.$isMessageEnabled) {
				credits = this.$rechargeApp.getCurrentSelectedPlanCredit();
				groups = this.$groupApp.getSelectedGroup();
				this.$option = 3;
			}
			else if(this.$isGroupEnabled) {
				groups = this.$groupApp.getSelectedGroup();
				this.$option = 1;
			}
			else {
				credits = this.$rechargeApp.getCurrentSelectedPlanCredit();
				this.$option = 2;
			}
				
			var $this = this;
			$.ajax({
						type : "POST",
						withCredentials : true,
						async : false,
						url : $this.$urlInput.val(),
						headers : {
							csrftoken : this.$csrf.getToken()
						},
						data : {
							csrfmiddlewaretoken : $this.$csrf.getToken(),
							amount : $this.$amtHidden.val(),
							refrenceno : $this.$refNoHidden.val(),
							credits : credits,
							nogroups : groups,
							option : $this.$option
						},
						success : function(json) {
							if (typeof (json.error) != 'undefined' && json.error != '') {
								$this.$couponApp.showError(json.error);
								event.stopPropagation();
							} else {
								$this.$secureAmt.val((json.token));
								$this.$form.submit();
							}
						},
						error : function(jqxhr, textStatus, errorThrown) {
							console.log(jqxhr);
							console.log(textStatus);
							console.log(errorThrown);
							$this.$applyBtn.button('reset');
							event.stopPropagation();
							return false;
						}
					});
		},
		getFormattedNo : function(number) {
			var num = number.toString();
			var afterPoint = '';
			if (num.indexOf('.') > 0)
				afterPoint = num.substring(num.indexOf('.'), num.length);
			num = Math.floor(num);
			num = num.toString();
			var lastThree = num.substring(num.length - 3);
			var otherNumbers = num.substring(0, num.length - 3);
			if (otherNumbers != '')
				lastThree = ',' + lastThree;
			return (otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree + afterPoint);
		},
		calculateTax : function(amount) {
			var tax_amount = parseFloat(amount*this.$tax_percantage/100);
			tax_amount = parseFloat(tax_amount.toFixed(2));
			return tax_amount;
		},
		addTaxToTotalAmount : function(amount) {
			var taxPercantage = 0;
			for (var i=0;i<this.$tax_percantage.length;i++) {
				taxPercantage += parseInt(this.$tax_percantage[i]);
			}
			var new_amount = parseFloat( amount + (amount*taxPercantage/100));
			new_amount = parseFloat(new_amount.toFixed(2));
			return new_amount; 
		},
		changeTotal : function() {
			var famt = 0.00;
			if(this.$isMessageEnabled)
				famt += this.$rechargeApp.getRecCalculatedAmt();
			if(this.$isGroupEnabled)
				famt += this.$groupApp.getGrpCalculatedAmt();
			
			this.$totalPriceBtn.text(this.addTaxToTotalAmount(famt));
			this.$totalPriceWithoutTax.text(famt);
			this.$amtHidden.val(this.addTaxToTotalAmount(famt).toFixed(2));
		},
		setNewAmount : function(new_amount) {
			this.$totalPriceBtn.text(this.addTaxToTotalAmount(new_amount));
			this.$totalPriceWithoutTax.text(new_amount);
			this.$amtHidden.val(this.addTaxToTotalAmount(new_amount).toFixed(2));
		},
		getTotalPriceWithoutTax : function() {
			var famt = 0.00;
			if(this.$isMessageEnabled)
				famt += this.$rechargeApp.getRecCalculatedAmt();
			if(this.$isGroupEnabled)
				famt += this.$groupApp.getGrpCalculatedAmt();
			return famt;
		},
		getCSRFToken : function() {
			return this.$csrf.getToken();
		},
		setTaxData : function (tax_labels, tax_percentage) {
			this.$tax_percantage = tax_percentage;
			this.$tax_label = tax_labels;
			var taxPercantage = "(";
			for (var i=0;i<this.$tax_percantage.length;i++) {
				taxPercantage += " + "
				taxPercantage += this.$tax_label[i];
				taxPercantage += " "
				taxPercantage += this.$tax_percantage[i];
				taxPercantage += "%"
			}
			taxPercantage += " ) "
			this.$taxPercantage.text(taxPercantage);
			CommonApp.changeTotal();
		},
	};
	window.CommonApp = CommonApp;
});