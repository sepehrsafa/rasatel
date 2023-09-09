/*
Template Name: DreamsChat - HTML Mobile Template
Author: Dreamguy's Technologies
Version: 1.1
*/


"use strict";

//Pre Loader
setTimeout(function () {
	$('.splash-screen').addClass('hide-screen');
}, 2000);

//Profile slider
if(jQuery('.media-col .swiper-container, .status-col .swiper-container').length > 0) {
	var swiper = new Swiper('.media-col .swiper-container, .status-col .swiper-container', {
		slidesPerView: 4.5,
		spaceBetween: 10,
	});
}

if(jQuery('[data-fancybox="gallery"]').length > 0) {
	$('[data-fancybox="gallery"]').fancybox({
	});
}

//Search visible
$('.search .search-icon ').on('click', function () {
	jQuery('.search_chat').addClass('show-search');
});
$('.search_chat .close-search ').on('click', function () {
	jQuery('.search_chat').removeClass('show-search');
});

//Search filter
$("#search-contact").on("keyup", function() {
	var value = $(this).val().toLowerCase();
	$(".chat-list-col ul li.person-list-item").filter(function() {
	  $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
	});
});