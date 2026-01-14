/*
Author       : Dreamguys
Template Name: Preskool - Bootstrap Admin Template
Version      : 1.0
*/

(function($) {
    "use strict";
	
	// Đảm bảo DOM đã sẵn sàng
	$(document).ready(function() {
	
	// Variables declarations
	
	var $wrapper = $('.main-wrapper');
	var $pageWrapper = $('.page-wrapper');
	var $slimScrolls = $('.slimscroll');
	
	// Sidebar
	
	var Sidemenu = function() {
		this.$menuItem = $('#sidebar-menu a');
	};
	
	function init() {
		var $this = Sidemenu;
		// Xóa event listener cũ để tránh duplicate
		$('#sidebar-menu a').off('click.sidemenu');
		// Gắn event listener mới với namespace
		$('#sidebar-menu a').on('click.sidemenu', function(e) {
			var $thisLink = $(this);
			var $parent = $thisLink.parent();
			var href = $thisLink.attr('href');
			
			// Loại bỏ # ở cuối URL nếu có
			if(href && typeof href === 'string' && href.endsWith('#')) {
				href = href.slice(0, -1);
				$thisLink.attr('href', href);
			}
			
			// Chỉ xử lý toggle cho menu cha có class 'submenu' và có href="#" hoặc rỗng
			// Cho phép các link con (không có class submenu) hoạt động bình thường
			if($parent.hasClass('submenu') && (href === '#' || !href || href === '' || href === 'javascript:void(0);')) {
				e.preventDefault();
				e.stopPropagation();
				
				if(!$thisLink.hasClass('subdrop')) {
					$('ul', $thisLink.parents('ul:first')).slideUp(350);
					$('a', $thisLink.parents('ul:first')).removeClass('subdrop');
					$thisLink.next('ul').slideDown(350);
					$thisLink.addClass('subdrop');
				} else if($thisLink.hasClass('subdrop')) {
					$thisLink.removeClass('subdrop');
					$thisLink.next('ul').slideUp(350);
				}
				return false;
			}
			// Nếu là link con (không phải menu cha), cho phép điều hướng bình thường
			// Đảm bảo không có overlay đang chặn
			if($('.sidebar-overlay.opened').length > 0) {
				$('.sidebar-overlay').removeClass('opened');
				$('html').removeClass('menu-opened');
				$wrapper.removeClass('slide-nav');
			}
		});
		$('#sidebar-menu ul li.submenu a.active').parents('li:last').children('a:first').addClass('active').trigger('click');
	}
	
	// Sidebar Initiate
	init();
	
	// Mobile menu sidebar overlay
	
	$('body').append('<div class="sidebar-overlay"></div>');
	$(document).on('click', '#mobile_btn', function() {
		$wrapper.toggleClass('slide-nav');
		$('.sidebar-overlay').toggleClass('opened');
		$('html').addClass('menu-opened');
		return false;
	});
	
	// Sidebar overlay - chỉ đóng khi click vào overlay, không ảnh hưởng sidebar
	$(document).on("click", ".sidebar-overlay.opened", function (e) {
		// Chỉ xử lý khi click trực tiếp vào overlay, không phải vào sidebar
		if ($(e.target).hasClass('sidebar-overlay')) {
			$wrapper.removeClass('slide-nav');
			$(".sidebar-overlay").removeClass("opened");
			$('html').removeClass('menu-opened');
		}
	});
	
	// Ngăn click event lan truyền từ sidebar ra overlay
	$('.sidebar').on('click', function(e) {
		// Chỉ stopPropagation cho các element không phải là link
		if(!$(e.target).is('a') && !$(e.target).closest('a').length) {
			e.stopPropagation();
		}
	});
	
	// Đảm bảo overlay không chặn click vào sidebar khi đóng
	// Và đóng overlay khi click vào bất kỳ link nào trong sidebar
	$(document).on('click', '.sidebar a', function(e) {
		var $link = $(this);
		var href = $link.attr('href');
		// Loại bỏ # ở cuối URL nếu có
		if(href && typeof href === 'string' && href.endsWith('#')) {
			href = href.slice(0, -1);
			$link.attr('href', href);
		}
		
		// Nếu overlay đang mở, đóng nó trước khi điều hướng
		if($('.sidebar-overlay.opened').length > 0) {
			$('.sidebar-overlay').removeClass('opened');
			$('html').removeClass('menu-opened');
			$wrapper.removeClass('slide-nav');
		}
	});
	
	// Đảm bảo overlay không chặn click vào page content
	$(document).on('click', '.page-wrapper a, .page-wrapper button, .page-wrapper input[type="submit"], .page-wrapper .btn', function(e) {
		// Nếu overlay đang mở, đóng nó
		if($('.sidebar-overlay.opened').length > 0) {
			$('.sidebar-overlay').removeClass('opened');
			$('html').removeClass('menu-opened');
			$wrapper.removeClass('slide-nav');
		}
	});
	
	// Đảm bảo khi load trang, overlay không bị mở
	$(window).on('load', function() {
		if($('.sidebar-overlay.opened').length > 0) {
			$('.sidebar-overlay').removeClass('opened');
			$('html').removeClass('menu-opened');
			$wrapper.removeClass('slide-nav');
		}
	});
	
	// Xử lý URL có # ở cuối - loại bỏ # khi load trang
	if(window.location.href.endsWith('#')) {
		var cleanUrl = window.location.href.slice(0, -1);
		window.history.replaceState({}, document.title, cleanUrl);
	}
	
	// Page Content Height
	
	if($('.page-wrapper').length > 0 ){
		var height = $(window).height();	
		$(".page-wrapper").css("min-height", height);
	}
	
	// Page Content Height Resize
	
	$(window).resize(function(){
		if($('.page-wrapper').length > 0 ){
			var height = $(window).height();
			$(".page-wrapper").css("min-height", height);
		}
	});
	
	// Select 2
	
    if ($('.select').length > 0) {
        $('.select').select2({
            minimumResultsForSearch: -1,
            width: '100%'
        });
    }
	
	// Datetimepicker
	
	if($('.datetimepicker').length > 0 ){
		$('.datetimepicker').datetimepicker({
			format: 'DD-MM-YYYY',
			icons: {
				up: "fas fa-angle-up",
				down: "fas fa-angle-down",
				next: 'fas fa-angle-right',
				previous: 'fas fa-angle-left'
			}
		});
		$('.datetimepicker').on('dp.show',function() {
			$(this).closest('.table-responsive').removeClass('table-responsive').addClass('temp');
		}).on('dp.hide',function() {
			$(this).closest('.temp').addClass('table-responsive').removeClass('temp')
		});
	}

	// Tooltip
	
	if($('[data-toggle="tooltip"]').length > 0 ){
		$('[data-toggle="tooltip"]').tooltip();
	}
	
    // Datatable

    if ($('.datatable').length > 0) {
        $('.datatable').DataTable({
            "bFilter": false,
        });
    }

	// Check all email
	
	$(document).on('click', '#check_all', function() {
		$('.checkmail').click();
		return false;
	});
	if($('.checkmail').length > 0) {
		$('.checkmail').each(function() {
			$(this).on('click', function() {
				if($(this).closest('tr').hasClass('checked')) {
					$(this).closest('tr').removeClass('checked');
				} else {
					$(this).closest('tr').addClass('checked');
				}
			});
		});
	}
	
	// Mail important
	
	$(document).on('click', '.mail-important', function() {
		$(this).find('i.fa').toggleClass('fa-star').toggleClass('fa-star-o');
	});
	
	// Summernote
	
	if($('.summernote').length > 0) {
		$('.summernote').summernote({
			height: 200,                 // set editor height
			minHeight: null,             // set minimum height of editor
			maxHeight: null,             // set maximum height of editor
			focus: false                 // set focus to editable area after initializing summernote
		});
	}
	
	
	// Sidebar Slimscroll

	if($slimScrolls.length > 0) {
		$slimScrolls.slimScroll({
			height: 'auto',
			width: '100%',
			position: 'right',
			size: '7px',
			color: '#ccc',
			allowPageScroll: false,
			wheelStep: 10,
			touchScrollStep: 100
		});
		var wHeight = $(window).height() - 60;
		$slimScrolls.height(wHeight);
		$('.sidebar .slimScrollDiv').height(wHeight);
		$(window).resize(function() {
			var rHeight = $(window).height() - 60;
			$slimScrolls.height(rHeight);
			$('.sidebar .slimScrollDiv').height(rHeight);
		});
	}
	
	// Small Sidebar

	$(document).on('click', '#toggle_btn', function() {
		if($('body').hasClass('mini-sidebar')) {
			$('body').removeClass('mini-sidebar');
			$('.subdrop + ul').slideDown();
		} else {
			$('body').addClass('mini-sidebar');
			$('.subdrop + ul').slideUp();
		}
		setTimeout(function(){ 
			mA.redraw();
			mL.redraw();
		}, 300);
		return false;
	});
	$(document).on('mouseover', function(e) {
		e.stopPropagation();
		if($('body').hasClass('mini-sidebar') && $('#toggle_btn').is(':visible')) {
			var targ = $(e.target).closest('.sidebar').length;
			if(targ) {
				$('body').addClass('expand-menu');
				$('.subdrop + ul').slideDown();
			} else {
				$('body').removeClass('expand-menu');
				$('.subdrop + ul').slideUp();
			}
			return false;
		}
	});

	// Circle Progress Bar
	function animateElements() {
		$('.circle-bar1').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph1').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph1').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
		$('.circle-bar2').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph2').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph2').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
		$('.circle-bar3').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph3').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph3').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
	}	
	
	if($('.circle-bar').length > 0) {
		animateElements();
	}
	$(window).scroll(animateElements);
	
	// Preloader
	
	$(window).on('load', function () {
		if($('#loader').length > 0) {
			$('#loader').delay(350).fadeOut('slow');
			$('body').delay(350).css({ 'overflow': 'visible' });
		}
	})
	
	}); // End document.ready
	
})(jQuery);