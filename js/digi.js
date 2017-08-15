if (typeof jQuery === 'undefined') {
	throw new Error('JavaScript requires jQuery')
}

/*
function loadMoviePosters() {

	jQuery('.poster-container a img').each( function(index) {
		var currentImage = jQuery(this);
		var title = currentImage.attr('movie-title').trim();
		var endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + title;

		jQuery.getJSON(endpoint, function(json) {
			if (json.results.length > 0) {
				currentImage.attr('src', 'https://image.tmdb.org/t/p/w500/' + json.results[0].poster_path);
			} else {
				currentImage.attr('src', '/images/placeholder.jpg');
			}
		});
	});
}
*/


/*
	Set the movie title and other hidden inputs when a poster is clicked on the Post Code page
*/
function setSelectedMovie() { 
	jQuery('.movie-link').click(function() { 
		var poster = jQuery(this).find('.poster-med');

		jQuery('#form-movie-id').val(poster.attr('movie-id'));
		jQuery('#form-poster-url').val(poster.attr('poster-url'));
		jQuery('#form-backdrop-url').val(poster.attr('backdrop-url'));
		jQuery('#form-movie-title').val(poster.attr('movie-title'));

		jQuery('#form-row').show();
	});
}



/*
	Initalizes the search bar to send out AJAX request with each key stroke
	Initializes both the nav search bar and the post code search bar
*/
function initSearchbar() { 
	jQuery('#results').hide();
	jQuery('#form-row').hide();

	/*
		This is for the search bar on the Post Code page
		It uses the MovieDB database to return results to the user
	*/
	if (jQuery('#movie').length > 0) { 
		jQuery('#movie').keyup(function() { 
			var query = jQuery('#movie').val();

			var endpoint = '';
			if ( jQuery('#movie-option').is(':checked') ) {
				endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + query;
			}
			else if ( jQuery('#collection-option').is(':checked') ) {
				endpoint = 'https://api.themoviedb.org/3/search/collection?api_key=f8bacc22524d435a1476adae350b4d41&query=' + query;
			}
			else if ( jQuery('#television-option').is(':checked') ) {
				endpoint = 'https://api.themoviedb.org/3/search/tv?api_key=f8bacc22524d435a1476adae350b4d41&query=' + query;
				// Get the tv id
				jQuery.ajax({
					url: endpoint,
					async: false
				}).done(function (json) {
					if (json.results.length > 0) {
						var tv_id = json.results[0].id;
						endpoint = 'https://api.themoviedb.org/3/tv/' + tv_id + '?api_key=f8bacc22524d435a1476adae350b4d41';
					}
				});
			}
			
			if (query.length > 0) {

				jQuery.getJSON(endpoint, function(json) { 
					
					jQuery('.poster-container a img').each( function(index) { 
						if (json.results && json.results.length >= index + 1) { 
							var result = json.results[index];
							
							jQuery(this).closest('.poster-column').show();
							if (result.poster_path) {

								jQuery(this).attr('movie-id', result.id);
								jQuery(this).attr('poster-url', result.poster_path);
								jQuery(this).attr('backdrop-url', result.backdrop_path);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + result.poster_path);

								if( jQuery('#movie-option').is(':checked') ) {
									jQuery(this).attr('movie-title', result.title);
									jQuery(this).siblings().find('.poster-title').text(result.title);
								}
								else if( jQuery('#collection-option').is(':checked') ) {
									jQuery(this).attr('movie-title', result.name);
									jQuery(this).siblings().find('.poster-title').text(result.name);
								}
							} else { 
								// If the image couldn't be loaded, remove the column from the results
								jQuery(this).closest('.poster-column').hide();
							}
						}

						// Is the search item a tv show? Then display the first result's seasons
						else if (json.seasons && json.seasons.length >= index + 1) {
							var season = json.seasons[index];

							jQuery(this).closest('.poster-column').show();
							if (season.poster_path) {

								jQuery(this).attr('movie-id', season.id);
								jQuery(this).attr('poster-url', season.poster_path);
								jQuery(this).attr('backdrop-url', json.backdrop_path);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + season.poster_path);
								jQuery(this).attr('movie-title', json.name + ' Season ' + season.season_number);
								jQuery(this).siblings().find('.poster-title').text(json.name + ' Season ' + season.season_number);

							} else {
								// If the image couldn't be loaded, remove the column from the results
								jQuery(this).closest('.poster-column').hide();
							}
						}
					});

					// Once the results have been loaded, hide any empty columns
					jQuery('.poster-med[poster-url=""]').each(function() {
						jQuery(this).closest('.poster-column').hide();
					})

					// Display the results!
					jQuery('#results').show();
				});

			} else { 
				jQuery('#results').hide();
			}
		});
	}

	/*
		This is for the search bar in nav bar of most pages
		It uses the site's ndb database to search among the movies that currently exist on the site
		These should probably be in two separate function but..meh..
	*/
	if(jQuery('#movie-search').length > 0) {
		var request = null;
		jQuery('#movie-search').keyup(/*jQuery.debounce(0,*/ function() { 
			var query = jQuery('#movie-search').val();
			var endpoint = '/ajaxcodesearch?q=' + query;

			var searchResults = [];
			jQuery('#movie-search').autocomplete({source: searchResults});
			if (query.length > 0) {
				// If a previous request is in progress when a new request is made, abort the previous request
				if (request != null) { 
					request.abort();
				}

				request = jQuery.getJSON(endpoint, function(json) {
				
					for (var i=0; i<10 && i<json.results.length; i++) { 
						var result = json.results[i].title;
						searchResults.push(result);
					}
				
					jQuery('#movie-search').autocomplete({source: searchResults});
				});
			} 
		});
	}
}


/*
	Presents a confirmation modal when user clicks to send a message
	The modal provides details on how the message with be sent and gives action choices (Send/Cancel)
*/
function validateMessageForm() { 
	if (jQuery("#messageform").length) {
		jQuery("#messageform").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



/*
	(Not currently doing anything I don't think)
	Will present confirmation modal when user is submiting a code for sale
*/
function validateCodeForm() { 
	if (jQuery("#action-button").length) {
		jQuery("#action-button").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



/*
	Set the details of the movie on the Code page
	Uses MovieDB to get the trailer URL, synopsis, runtime, release date, etc.
*/
function setCodeDetails() { 
	if (jQuery("#details-trailer").length > 0) { 
		jQuery("#details-trailer").hide();

		var movieid = jQuery("body").attr("movieid");
		var video_base_url = "https://www.youtube.com/embed/";
		var video_options = "?modestbranding=1&autohide=1&showinfo=0&controls=0";
		var imdb_base_url = "https://www.imdb.com/title/";
		var rotten_base_url = "https://www.rottentomatoes.com/m/";
		var video_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "/videos?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
		var movie_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
	
		jQuery.getJSON(video_endpoint, function(json) { 

			if (json.results.length > 0) {
				var video_key = json.results[0].key;
				jQuery('#details-trailer').attr('src', video_base_url + video_key + video_options);
				
				jQuery('#details-trailer').show();
			}
		});

		jQuery.getJSON(movie_endpoint, function(json) { 
			
			if (json) {
				jQuery('#details-synopsis').text(json.overview);
				jQuery('#details-runtime').text(json.runtime + " minutes");
				jQuery('#details-release').text(new Date(json.release_date).toDateString());
				jQuery('#imdb-link').attr('href', imdb_base_url + json.imdb_id);
				jQuery('#rotten-link').attr('href', rotten_base_url + json.title.replace(/[ ·-]/g, "_").replace(/[:'.,!?]/g, ""));
			}
		});
	}
}


/*

*/
function initCodeTypeRadio() {
	jQuery('input[type=radio][name="code-type"]').change( function() {
		jQuery('#results').hide();
		jQuery('#movie').val('');
		jQuery('#form-row').hide();

		if (jQuery(this).attr('id') === 'movie-option') {
			jQuery('#movie').attr('placeholder', 'search for a movie');
		}
		else if (jQuery(this).attr('id') === 'collection-option') {
			jQuery('#movie').attr('placeholder', 'search for a collection');
		}
		else if (jQuery(this).attr('id') === 'television-option') {
			jQuery('#movie').attr('placeholder', 'search for a tv show');
		}
	});
}



jQuery(document).ready( function() {

	initSearchbar();
	initCodeTypeRadio();
	setSelectedMovie();
	setCodeDetails();
	validateMessageForm();
	validateCodeForm();

});