'use strict';

$(document).ready(function() {
	console.log('=== CHART DATA SCRIPT LOADED ===');
	console.log('ApexCharts available:', typeof ApexCharts !== 'undefined');
	console.log('jQuery available:', typeof $ !== 'undefined');
	console.log('Document ready state:', document.readyState);

	// 1. Biểu đồ phân bố học sinh theo lớp (Pie Chart)
	console.log('=== INITIALIZING CHARTS ===');
	console.log('1. Checking for chart-class-distribution element...');
	if ($('#chart-class-distribution').length > 0) {
		console.log('✓ Found chart-class-distribution element');
		var classDistributionScript = document.getElementById('class-distribution');
		var classDistributionData = [];
		
		if (classDistributionScript) {
			console.log('Found class-distribution script element');
			try {
				var rawData = classDistributionScript.textContent;
				console.log('Raw class distribution data:', rawData);
				classDistributionData = JSON.parse(rawData);
				console.log('Parsed Class Distribution Data:', classDistributionData);
			} catch (e) {
				console.error('Error parsing class distribution data:', e);
				console.error('Raw data:', classDistributionScript.textContent);
			}
		} else {
			console.warn('Class distribution script element not found');
		}
		
		if (classDistributionData && classDistributionData.length > 0) {
			var options = {
				chart: {
					type: 'pie',
					height: 350
				},
				series: classDistributionData.map(item => item.value),
				labels: classDistributionData.map(item => item.name),
				colors: ['#FFBC53', '#19affb', '#5e72e4', '#2dce89', '#f5365c', '#fb6340', '#ffd600', '#11cdef'],
				legend: {
					position: 'bottom'
				},
				tooltip: {
					y: {
						formatter: function (val) {
							return val + " học sinh";
						}
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-class-distribution"), options);
			chart.render();
			console.log('Class distribution chart rendered');
		} else {
			console.warn('No class distribution data, showing placeholder');
			$('#chart-class-distribution').html('<div class="text-center text-muted p-5"><i class="fas fa-chart-pie fa-3x mb-3"></i><p>Chưa có dữ liệu</p></div>');
		}
		} else {
			console.warn('✗ chart-class-distribution element NOT FOUND');
		}

	// 2. Biểu đồ điểm trung bình theo môn học (Bar Chart)
	if ($('#chart-subject-grades').length > 0) {
		var subjectGradesScript = document.getElementById('subject-avg-grades');
		var subjectData = [];
		var subjectLabels = [];
		
		if (subjectGradesScript) {
			try {
				var data = JSON.parse(subjectGradesScript.textContent);
				subjectData = data.map(item => item.avg);
				subjectLabels = data.map(item => item.name);
				console.log('Subject Grades Data:', data);
			} catch (e) {
				console.error('Error parsing subject grades data:', e);
			}
		} else {
			console.warn('Subject grades script element not found');
		}
		
		if (subjectData && subjectData.length > 0) {
			var options = {
				chart: {
					type: 'bar',
					height: 350,
					toolbar: {
						show: false
					}
				},
				plotOptions: {
					bar: {
						horizontal: false,
						columnWidth: '55%',
						endingShape: 'rounded'
					}
				},
				dataLabels: {
					enabled: false
				},
				stroke: {
					show: true,
					width: 2,
					colors: ['transparent']
				},
				series: [{
					name: 'Điểm trung bình',
					data: subjectData
				}],
				xaxis: {
					categories: subjectLabels,
					labels: {
						rotate: -45,
						rotateAlways: false
					}
				},
				yaxis: {
					title: {
						text: 'Điểm'
					},
					min: 0,
					max: 10
				},
				fill: {
					opacity: 1,
					colors: ['#19affb']
				},
				tooltip: {
					y: {
						formatter: function (val) {
							return val.toFixed(2) + " điểm";
						}
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-subject-grades"), options);
			chart.render();
		} else {
			$('#chart-subject-grades').html('<p class="text-center text-muted p-4">Chưa có dữ liệu</p>');
		}
	}

	// 3. Biểu đồ phân bố điểm số (Pie Chart)
	if ($('#chart-grade-distribution').length > 0) {
		var gradeDistributionScript = document.getElementById('grade-distribution');
		var gradeDistributionData = [];
		
		if (gradeDistributionScript) {
			try {
				gradeDistributionData = JSON.parse(gradeDistributionScript.textContent);
				console.log('Grade Distribution Data:', gradeDistributionData);
			} catch (e) {
				console.error('Error parsing grade distribution data:', e);
			}
		} else {
			console.warn('Grade distribution script element not found');
		}
		
		if (gradeDistributionData && gradeDistributionData.length > 0) {
			var gradeColors = {
				'A+': '#2dce89',
				'A': '#5e72e4',
				'B+': '#19affb',
				'B': '#11cdef',
				'C+': '#ffd600',
				'C': '#fb6340',
				'D': '#f5365c',
				'F': '#e74c3c'
			};
			
			var options = {
				chart: {
					type: 'donut',
					height: 350
				},
				series: gradeDistributionData.map(item => item.value),
				labels: gradeDistributionData.map(item => item.name),
				colors: gradeDistributionData.map(item => gradeColors[item.name] || '#777'),
				legend: {
					position: 'bottom'
				},
				tooltip: {
					y: {
						formatter: function (val) {
							return val + " bài";
						}
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-grade-distribution"), options);
			chart.render();
		} else {
			$('#chart-grade-distribution').html('<p class="text-center text-muted p-4">Chưa có dữ liệu</p>');
		}
	}

	// 4. Biểu đồ tỷ lệ điểm danh (7 ngày gần nhất) (Line Chart)
	if ($('#chart-attendance').length > 0) {
		var attendanceDataScript = document.getElementById('attendance-chart-data');
		var attendanceLabelsScript = document.getElementById('attendance-chart-labels');
		var attendanceData = [];
		var attendanceLabels = [];
		
		if (attendanceDataScript && attendanceLabelsScript) {
			try {
				attendanceData = JSON.parse(attendanceDataScript.textContent);
				attendanceLabels = JSON.parse(attendanceLabelsScript.textContent);
				console.log('Attendance Data:', attendanceData);
				console.log('Attendance Labels:', attendanceLabels);
			} catch (e) {
				console.error('Error parsing attendance data:', e);
			}
		} else {
			console.warn('Attendance script elements not found');
		}
		
		if (attendanceData && attendanceData.length > 0) {
			var options = {
				chart: {
					height: 350,
					type: "line",
					toolbar: {
						show: false
					}
				},
				dataLabels: {
					enabled: false
				},
				stroke: {
					curve: "smooth",
					width: 3
				},
				series: [{
					name: "Tỷ lệ điểm danh (%)",
					data: attendanceData
				}],
				xaxis: {
					categories: attendanceLabels
				},
				yaxis: {
					min: 0,
					max: 100,
					title: {
						text: 'Tỷ lệ (%)'
					},
					labels: {
						formatter: function (val) {
							return val.toFixed(0) + "%";
						}
					}
				},
				colors: ['#FFBC53'],
				tooltip: {
					y: {
						formatter: function (val) {
							return val.toFixed(2) + "%";
						}
					}
				},
				markers: {
					size: 5,
					hover: {
						size: 7
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-attendance"), options);
			chart.render();
		} else {
			$('#chart-attendance').html('<p class="text-center text-muted p-4">Chưa có dữ liệu</p>');
		}
	}

	// 5. Biểu đồ phân bố học sinh theo giới tính (Pie Chart)
	if ($('#chart-gender-distribution').length > 0) {
		var genderDistributionScript = document.getElementById('gender-distribution');
		var genderDistributionData = [];
		
		if (genderDistributionScript) {
			try {
				genderDistributionData = JSON.parse(genderDistributionScript.textContent);
				console.log('Gender Distribution Data:', genderDistributionData);
			} catch (e) {
				console.error('Error parsing gender distribution data:', e);
			}
		} else {
			console.warn('Gender distribution script element not found');
		}
		
		if (genderDistributionData && genderDistributionData.length > 0) {
			var genderColors = {
				'Nam': '#19affb',
				'Nữ': '#f5365c',
				'Khác': '#5e72e4'
			};
			
			var options = {
				chart: {
					type: 'pie',
					height: 350
				},
				series: genderDistributionData.map(item => item.value),
				labels: genderDistributionData.map(item => item.name),
				colors: genderDistributionData.map(item => genderColors[item.name] || '#777'),
				legend: {
					position: 'bottom'
				},
				tooltip: {
					y: {
						formatter: function (val) {
							return val + " học sinh";
						}
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-gender-distribution"), options);
			chart.render();
		} else {
			$('#chart-gender-distribution').html('<p class="text-center text-muted p-4">Chưa có dữ liệu</p>');
		}
	}

	// 6. Biểu đồ số lượng học sinh theo lớp (Bar Chart)
	if ($('#chart-class-student-count').length > 0) {
		var classStudentCountScript = document.getElementById('class-student-count');
		var classData = [];
		var classLabels = [];
		
		if (classStudentCountScript) {
			try {
				var data = JSON.parse(classStudentCountScript.textContent);
				classData = data.map(item => item.count);
				classLabels = data.map(item => item.name);
				console.log('Class Student Count Data:', data);
			} catch (e) {
				console.error('Error parsing class student count data:', e);
			}
		} else {
			console.warn('Class student count script element not found');
		}
		
		if (classData && classData.length > 0) {
			var options = {
				chart: {
					type: 'bar',
					height: 350,
					toolbar: {
						show: false
					}
				},
				plotOptions: {
					bar: {
						horizontal: false,
						columnWidth: '55%',
						endingShape: 'rounded'
					}
				},
				dataLabels: {
					enabled: true,
					formatter: function (val) {
						return val;
					}
				},
				stroke: {
					show: true,
					width: 2,
					colors: ['transparent']
				},
				series: [{
					name: 'Số lượng học sinh',
					data: classData
				}],
				xaxis: {
					categories: classLabels,
					labels: {
						rotate: -45,
						rotateAlways: false
					}
				},
				yaxis: {
					title: {
						text: 'Số lượng'
					}
				},
				fill: {
					opacity: 1,
					colors: ['#5e72e4']
				},
				tooltip: {
					y: {
						formatter: function (val) {
							return val + " học sinh";
						}
					}
				}
			};
			var chart = new ApexCharts(document.querySelector("#chart-class-student-count"), options);
			chart.render();
		} else {
			$('#chart-class-student-count').html('<p class="text-center text-muted p-4">Chưa có dữ liệu</p>');
		}
	}

});
