$(function(){
	
	$('.go_analysis').click(function(){
		text_gene_list = $(this).prev("div").prev("div").text();
		$('#gene_list').val(text_gene_list);
		text_exp = $(this).prev("div").prev("div").prev("div").text();
		$('#exp').val(text_exp)
		
	});
});