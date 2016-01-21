<!DOCTYPE html>
<html lang="en">
	<head>
		<title>MLS Table</title>
		<meta charset="utf-8" />
		<meta name="description" content="MLS Results" />
		<meta name="keywords" content="major league soccer" />
		
		<link rel="stylesheet" type="text/css" href="main.css" />
		<link rel="stylesheet" type="text/css" href="sorter_green_style.css" />
		<link rel="icon" type="image/png" href="favicon.png" />
		<script src="jquery-2.0.3.min.js"></script> 
		<script src="jquery.tablesorter.js"></script>
		<script src="tooltipscript.js"></script>
		<script type="text/javascript">
			$(document).ready(
				function() { 
					$("#leader").tablesorter(
						{
							sortList: [[1,1],[16,1],[0,0]],
							widgets: ['zebra']
						}
					); 
				} 
			);
		</script>
	</head>
	<body>
		<div id="frame">
			<div id="main">
				<div class="header">
					<?php include 'header.html' ?>
				</div>
				<div class="textHead">
					MLS TABLE
				</div>
				<div class="options">
					 
					<!-- select year(s) drop down, pass year on or -1 for all -->
					<!-- Season: <select id="yearPicker" onChange=setYear(this.value)>
						<option value=-1>All</option>
						<option value=2007>2007</option>
						<option value=2008>2008</option>
						<option value=2009>2009</option>
						<option value=2010>2010</option>
						<option value=2011>2011</option>
						<option value=2012>2012</option>
						<option value=2013>2013</option>
						<option value=2014 selected="selected">2014</option>
					</select> -->			
				</div>
				<div class="leaderboard" id="leaderboard">
					<table id="leader" class="tablesorter" cellspacing="1">
						<thead>
							<tr style="background-color: white;">
								<td align="center" colspan="2">Basic Info</td>
								<td align="center" colspan="4">Totals</td>
								<td align="center" colspan="4">Home</td>
								<td align="center" colspan="4">Road</td>
								<td align="center" colspan="3">Projected</td>
							</tr>
							<tr>
								<th>Team</th>
								<th>Conf</th>
								<th>GP</th>
								<th>GS</th>
								<th>GA</th>
								<th>Pts</th>
								<th>GP</th>
								<th>GS</th>
								<th>GA</th>
								<th>Pts</th>
								<th>GP</th>
								<th>GS</th>
								<th>GA</th>
								<th>Pts</th>
								<th>Home</th>
								<th>Road</th>
								<th>Total</th>
							</tr>
						</thead>
						<tbody>
						</tbody>
					</table>			
				</div>

				<script type="text/javascript">	
					var byYearCache = {};
					var jsonCache = {};
					var allRows = new Array(); //ArrayList<String>
					var sorting = [[1,1],[16,1],[0,0]];
					var yearFilter = new Date().getFullYear();
					if (new Date().getMonth() < 2) {
						//too early
						yearFilter--;
					}

			        function buildAllRows() {
	                    for (yr in jsonCache) {
	                        byYearCache[yr] = new Array();
	                        var entries = jsonCache[yr];
	                        for (entry in entries) {
	                        	var csvStr = jsonObjToEntryRow(entries[entry]);
	                        	allRows.push(csvStr);
	                        	byYearCache[yr].push(csvStr);
	                        }
	                    }
	                }

			        function jsonObjToEntryRow(json) {
			        	var csvStr = "";
			        	csvStr+= json["name"] + ",";
			        	csvStr+= json["conference"] + ",";
			        	csvStr+= json["games_played"] + ",";
			        	csvStr+= json["goals_scored"] + ",";
			        	csvStr+= json["goals_allowed"] + ",";
			        	csvStr+= json["points"] + ",";
			        	csvStr+= json["home_games_played"] + ",";
			        	csvStr+= json["home_goals_scored"] + ",";
			        	csvStr+= json["home_goals_allowed"] + ",";
			        	csvStr+= json["home_points"] + ",";
			        	csvStr+= json["road_games_played"] + ",";
			        	csvStr+= json["road_goals_scored"] + ",";
			        	csvStr+= json["road_goals_allowed"] + ",";
			        	csvStr+= json["road_points"] + ",";
			        	csvStr+= json["proj_home_points"] + ",";
			        	csvStr+= json["proj_road_points"] + ",";
			        	csvStr+= (json["proj_home_points"] + json["proj_road_points"]);
			        	return csvStr;
			        }

			        function loadTable() {
						emptyTable();				
						if (yearFilter > 0){
							var rows = byYearCache[yearFilter];
							for (var i = 0; i < rows.length; i++) {
								var row = rows[i];
								addRowToLeaderBoard(row);
							}
						}
						else {
							for (var i = 0; i < allRows.length; i++) {
								var row = allRows[i];
								addRowToLeaderBoard(row);
							}
						}
						$("#leader").trigger("update");
						setTimeout(
							function() {
								$("#leader").trigger("sorton", [sorting]);
							}, 10
						);
					}

			        function emptyTable() {
						$("#leader > tbody").empty();
					}
					function setYear(year) { yearFilter = year; loadTable(); }

					function addRowToLeaderBoard(row) {
						var tds = row.split(",");
						var append = "<tr>";

						append+="<td>" + tds[0] + "</td>";
						append+="<td>" + tds[1] + "</td>";
						for (var i = 2; i < tds.length; i++) {
							var number = parseFloat(tds[i]);
							number = number.toFixed(0);
							append+="<td align='right'>" + number + "</td>";
						}
						append+= "</tr>";
						$('#leader > tbody:last').append(append);
					}

			        $.getJSON( "/cache/mls_table.cache", function(data) {
			        	jsonCache = data.year;
			        	buildAllRows();
			        	loadTable();
					});
				</script>
			</div>
		</div>
	</body>
</html>
