# generated by:
# eu4/generate_maps.py --generate-provincelists
from eu4.paths import verified_for_version
verified_for_version('1.36.1')
coastal_provinces = [1,2,3,6,9,11,12,13,14,15,16,17,19,20,21,23,24,25,26,27,28,30,33,34,35,36,37,38,39,40,41,43,44,45,46,47,48,54,55,87,89,90,96,97,98,99,100,101,102,111,112,113,114,115,117,118,119,120,121,122,123,124,125,126,127,130,136,137,142,143,144,145,146,147,148,151,159,163,164,167,168,169,170,171,172,173,174,197,200,201,206,207,209,212,213,220,221,222,223,224,226,227,229,230,231,233,234,235,236,238,239,241,242,243,244,246,247,248,249,251,252,253,282,284,285,286,287,313,315,316,317,318,319,320,321,325,327,328,330,333,334,335,337,338,339,341,342,345,347,353,354,355,356,357,358,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,378,387,388,389,394,395,396,397,398,399,400,401,402,408,412,430,431,462,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,517,529,530,531,534,535,536,537,539,540,543,549,552,561,564,568,572,574,575,579,586,590,591,593,594,595,596,597,598,599,603,605,606,607,610,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,665,666,667,668,669,684,685,690,695,704,729,732,733,735,736,737,738,741,743,744,745,746,747,748,749,751,753,754,755,756,757,760,761,762,763,764,766,769,772,773,778,779,780,781,782,783,784,786,787,788,789,792,793,796,805,806,809,812,816,819,823,826,828,829,830,831,833,835,836,837,838,839,840,841,843,844,845,846,847,848,849,851,854,855,858,859,862,865,866,868,869,871,872,873,874,884,888,893,921,922,923,926,927,928,929,932,938,950,952,953,957,962,965,967,968,970,971,972,973,974,975,976,977,978,979,980,981,982,983,984,985,986,994,995,996,997,998,999,1000,1003,1004,1005,1006,1012,1013,1014,1015,1016,1017,1018,1019,1021,1022,1023,1024,1025,1026,1027,1028,1030,1031,1032,1033,1034,1035,1041,1043,1044,1047,1048,1050,1084,1085,1086,1087,1090,1092,1094,1095,1096,1097,1098,1099,1100,1101,1102,1103,1104,1105,1106,1107,1108,1109,1110,1111,1112,1113,1114,1118,1119,1126,1139,1141,1147,1151,1163,1164,1165,1166,1167,1168,1172,1174,1175,1177,1179,1180,1181,1182,1183,1186,1192,1193,1194,1195,1196,1197,1198,1199,1200,1201,1202,1203,1204,1205,1206,1209,1212,1215,1230,1232,1235,1236,1237,1238,1239,1240,1241,1242,1243,1244,1245,1246,1247,1248,1306,1744,1745,1749,1750,1751,1756,1764,1773,1774,1775,1776,1777,1815,1816,1818,1819,1820,1822,1824,1825,1826,1829,1830,1837,1839,1842,1845,1847,1850,1851,1852,1854,1855,1856,1858,1860,1865,1874,1881,1882,1930,1931,1933,1934,1935,1955,1974,1978,1979,1981,1982,1983,1984,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2002,2010,2013,2021,2022,2024,2025,2026,2029,2030,2038,2039,2043,2051,2052,2080,2084,2089,2100,2101,2103,2106,2112,2113,2138,2139,2142,2145,2148,2149,2154,2155,2156,2157,2159,2160,2161,2195,2196,2219,2231,2233,2239,2241,2242,2258,2290,2294,2296,2297,2298,2299,2302,2304,2313,2315,2320,2321,2324,2325,2326,2329,2331,2333,2340,2341,2342,2346,2347,2348,2372,2373,2374,2376,2377,2387,2390,2391,2392,2393,2394,2402,2403,2404,2406,2410,2412,2440,2447,2451,2452,2453,2455,2461,2469,2470,2473,2476,2477,2481,2484,2485,2499,2516,2530,2533,2534,2535,2536,2539,2542,2543,2546,2547,2550,2554,2560,2561,2566,2568,2569,2570,2572,2573,2574,2575,2576,2577,2578,2582,2583,2592,2609,2610,2611,2612,2613,2616,2620,2627,2630,2631,2632,2633,2634,2636,2637,2638,2639,2640,2641,2647,2648,2649,2650,2651,2652,2653,2654,2655,2656,2657,2658,2659,2660,2663,2664,2665,2668,2673,2674,2675,2677,2678,2679,2680,2682,2683,2684,2685,2686,2688,2689,2690,2691,2692,2693,2694,2695,2696,2697,2698,2699,2700,2701,2702,2703,2704,2705,2706,2708,2709,2710,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,2730,2731,2732,2733,2734,2735,2736,2737,2738,2739,2741,2742,2743,2744,2745,2752,2753,2765,2774,2775,2782,2783,2786,2788,2789,2790,2793,2794,2795,2796,2803,2806,2807,2808,2819,2820,2821,2822,2826,2828,2840,2841,2848,2850,2851,2857,2862,2868,2869,2873,2874,2886,2887,2890,2912,2921,2927,2929,2935,2938,2954,2977,2980,2982,2983,2984,2985,2986,2988,2992,2994,2995,2996,2999,3003,4020,4021,4022,4024,4025,4026,4028,4029,4031,4032,4049,4078,4079,4080,4110,4111,4113,4118,4119,4121,4130,4131,4141,4142,4143,4144,4145,4149,4163,4165,4174,4175,4180,4181,4182,4183,4184,4185,4186,4187,4189,4190,4192,4193,4194,4196,4216,4227,4228,4230,4231,4257,4258,4268,4269,4278,4279,4283,4284,4286,4316,4327,4332,4349,4350,4351,4352,4353,4354,4355,4356,4359,4360,4361,4362,4363,4364,4365,4367,4368,4369,4371,4373,4374,4375,4378,4380,4381,4382,4383,4385,4386,4399,4407,4408,4409,4410,4413,4415,4416,4417,4418,4419,4427,4429,4430,4441,4454,4455,4457,4474,4475,4477,4512,4546,4548,4549,4550,4554,4555,4556,4559,4560,4561,4562,4563,4564,4565,4576,4577,4578,4580,4589,4592,4593,4595,4596,4597,4598,4599,4604,4610,4611,4612,4616,4618,4619,4620,4621,4622,4623,4624,4625,4626,4637,4639,4649,4651,4652,4656,4658,4696,4698,4699,4700,4701,4705,4706,4729,4732,4733,4735,4736,4737,4738,4745,4746,4752,4753,4754,4779,4787,4790,4791,4792,4794,4795,4796,4797,4798,4799,4800,4801,4802,4804,4805,4809,4810,4811,4813,4815,4816,4817,4818,4819,4821,4822,4825,4826,4830,4831,4845,4846,4847,4848,4849,4850,4851,4854,4857,4858,4864,4865,4866,4867,4868,4869,4891,4934,4935,4936,4937,4938,4939]
is_island = [25,126,163,320,321,367,368,481,482,483,487,491,492,493,501,574,634,645,651,979,1015,1095,1096,1097,1098,1099,1100,1101,1102,1103,1235,1236,1238,1239,1241,1243,1244,1248,1306,1881,1978,1979,1981,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2002,2025,2679,2683,2684,2696,2717,2725,2741,4020,4365,4651]
province_is_on_an_island = [12,14,25,35,112,124,125,126,127,142,163,164,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,320,321,333,366,367,368,369,370,371,372,373,374,375,376,396,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,572,574,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,666,738,972,979,980,981,982,983,1012,1014,1015,1017,1018,1019,1020,1021,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1085,1095,1096,1097,1098,1099,1100,1101,1102,1103,1104,1105,1106,1107,1108,1109,1193,1194,1201,1235,1236,1237,1238,1239,1240,1241,1242,1243,1244,1245,1246,1247,1248,1306,1792,1818,1819,1820,1825,1830,1832,1835,1837,1839,1843,1847,1852,1860,1861,1881,1930,1978,1979,1981,1983,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2002,2022,2025,2099,2100,2154,2155,2160,2348,2573,2578,2654,2655,2656,2658,2659,2673,2674,2675,2676,2677,2678,2679,2680,2681,2682,2683,2684,2685,2686,2687,2688,2689,2690,2691,2692,2693,2695,2696,2697,2698,2699,2700,2701,2702,2703,2704,2705,2706,2707,2708,2709,2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2728,2737,2738,2739,2741,2954,2982,2986,2999,3003,4020,4021,4022,4023,4024,4025,4026,4027,4028,4029,4030,4031,4032,4110,4118,4119,4120,4121,4130,4131,4180,4181,4182,4183,4184,4185,4186,4187,4188,4189,4190,4191,4192,4193,4348,4349,4350,4351,4352,4353,4354,4355,4356,4359,4360,4361,4362,4363,4364,4365,4366,4367,4368,4369,4370,4371,4372,4373,4374,4375,4376,4377,4378,4379,4380,4407,4408,4409,4559,4560,4565,4618,4619,4620,4621,4622,4623,4624,4651,4658,4698,4700,4735,4736,4737,4745,4785,4790,4791,4792,4793,4794,4795,4796,4797,4798,4799,4800,4801,4802,4803,4804,4805,4806,4809,4810,4811,4816,4817,4818,4845,4868,4869,4934,4935,4936,4937,4938,4939]
island = [12,14,25,35,112,126,142,163,164,253,320,321,333,366,367,368,369,396,481,482,483,487,491,492,493,494,495,496,497,498,499,500,501,502,574,631,632,633,634,645,646,647,648,649,650,651,659,972,979,982,983,1015,1032,1095,1096,1097,1098,1099,1100,1101,1102,1103,1201,1235,1236,1238,1239,1240,1241,1242,1243,1244,1247,1248,1306,1881,1930,1978,1979,1981,1983,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2002,2022,2025,2348,2578,2678,2679,2683,2684,2686,2692,2693,2696,2700,2716,2717,2725,2728,2741,2954,2999,3003,4020,4350,4351,4352,4364,4365,4559,4560,4565,4651,4698,4700,4745,4934,4935,4936,4937,4938]
terrain_to_provinces = {
    "glacier": [1034,1035,1104,1105,2025,2074,2128,2440,2574],
    "farmlands": [6,12,14,43,44,45,64,65,67,68,70,77,78,88,90,92,97,98,100,104,108,109,113,115,117,118,121,125,134,146,148,150,151,152,153,160,161,167,169,172,177,180,182,183,186,191,192,200,234,235,236,238,243,245,248,254,255,257,258,259,260,262,264,266,267,268,279,280,289,290,358,359,361,363,410,415,506,507,510,522,523,524,532,540,555,556,558,561,563,581,584,585,586,600,613,665,667,671,672,679,682,683,684,685,687,688,690,691,692,695,696,700,735,916,917,920,925,930,1020,1021,1028,1030,1744,1767,1772,1816,1821,1822,1836,1838,1841,1862,1865,1868,1874,1876,1877,1879,1954,2026,2033,2044,2045,2047,2060,2063,2075,2076,2095,2137,2138,2139,2140,2141,2142,2143,2144,2145,2148,2149,2150,2151,2156,2157,2159,2163,2172,2175,2176,2310,2312,2316,2380,2407,2532,2745,2753,2774,2775,2794,2796,2955,2957,2979,2980,2981,2998,4126,4173,4194,4195,4196,4197,4212,4213,4240,4316,4367,4368,4371,4375,4382,4383,4384,4388,4390,4392,4396,4415,4416,4428,4476,4479,4487,4489,4490,4496,4497,4510,4513,4529,4531,4538,4712,4765,4769,4831,4832],
    "forest": [2,4,5,8,9,10,11,17,18,19,29,30,31,32,305,309,312,313,314,315,908,910,960,978,980,990,991,993,996,997,998,1001,1002,1007,1009,1011,1026,1036,1037,1038,1039,1040,1041,1042,1044,1045,1046,1054,1059,1061,1067,1069,1070,1072,1073,1077,1080,1109,1755,1776,1777,1780,1813,1955,1958,1961,1962,1963,1964,2015,2022,2430,2431,2436,2437,2438,2439,2445,2512,2517,2572,2573,2575,2576,2581,2582,2583,2588,2589,2590,2591,2593,2594,2595,2601,2603,2611,2671,4113,4114,4122,4123,4124,4129,4151,4152,4187,4256,4257,4258,4259,4261,4262,4263,4662,4691,4786,4871,4873,4874,4875,4876,4877,4878,4880,4883,4884,4885,4887,4888,4889,4890,4892,4893,4894,4895,4896,4897,4899,4907,4912,4913,4914,4921,4922],
    "hills": [16,21,63,101,102,105,106,107,111,116,119,123,133,137,140,156,165,176,193,196,197,198,201,203,212,232,242,250,251,318,325,488,489,508,509,511,515,518,521,525,527,529,530,531,533,538,545,548,550,554,557,559,604,608,609,611,615,652,657,658,669,670,681,686,733,740,837,839,841,844,847,849,851,854,855,899,911,931,935,949,951,959,961,964,966,969,972,981,986,992,994,995,1016,1018,1022,1025,1029,1106,1108,1117,1121,1746,1770,1774,1792,1820,1823,1824,1827,1828,1829,1830,1832,1833,1840,1843,1844,1848,1852,1856,1869,1870,1934,1947,1949,1951,2011,2012,2023,2027,2030,2032,2036,2037,2040,2043,2056,2058,2069,2070,2071,2080,2083,2089,2090,2092,2097,2146,2147,2152,2153,2158,2171,2173,2174,2299,2373,2379,2382,2479,2509,2515,2518,2527,2531,2548,2552,2553,2555,2556,2557,2558,2559,2562,2563,2565,2567,2571,2577,2579,2580,2606,2607,2627,2638,2640,2642,2648,2653,2657,2658,2660,2694,2697,2698,2701,2715,2738,2742,2744,2818,2956,2965,2967,2976,2977,2978,2983,2984,2987,2991,2992,3002,4023,4046,4050,4063,4066,4068,4069,4070,4072,4098,4102,4144,4145,4164,4180,4183,4185,4188,4191,4192,4229,4231,4239,4307,4311,4312,4315,4361,4362,4363,4366,4414,4420,4425,4426,4427,4429,4430,4434,4449,4453,4459,4462,4465,4466,4467,4480,4483,4484,4485,4491,4492,4493,4500,4511,4552,4570,4571,4572,4573,4574,4581,4603,4607,4609,4636,4640,4646,4694,4695,4696,4702,4705,4707,4715,4739,4744,4753,4761,4762,4764,4777,4779,4840,4845,4856,4939],
    "woods": [3,34,37,38,40,41,46,47,48,49,50,51,52,53,56,57,58,59,60,61,62,66,69,72,80,81,82,83,84,85,86,93,94,95,99,128,129,130,141,173,174,175,178,181,184,187,188,189,190,194,195,206,239,240,244,247,256,261,269,271,272,273,274,275,276,296,297,298,306,307,310,311,316,317,372,374,375,376,480,727,731,767,770,771,859,873,874,895,912,914,918,919,933,934,937,939,940,941,943,944,945,946,947,948,954,955,956,958,963,965,967,968,970,971,973,984,985,987,988,989,1014,1027,1033,1049,1050,1053,1056,1060,1062,1063,1064,1065,1068,1074,1079,1083,1084,1107,1742,1752,1753,1754,1758,1759,1760,1761,1762,1763,1765,1769,1819,1826,1834,1835,1851,1857,1863,1866,1875,1878,1880,1937,1938,1945,1956,1957,1959,1960,1972,1982,1985,2010,2013,2014,2102,2106,2304,2423,2424,2427,2428,2429,2432,2433,2435,2442,2443,2446,2482,2487,2521,2522,2523,2524,2525,2526,2528,2529,2540,2541,2544,2545,2549,2551,2560,2566,2568,2569,2570,2584,2585,2586,2587,2639,2665,2670,2737,2739,2749,2750,2963,2964,2969,2970,2971,2972,2973,2974,2975,2993,2995,2996,2997,3000,4112,4115,4116,4117,4118,4119,4120,4121,4127,4148,4165,4166,4176,4181,4182,4184,4186,4189,4241,4242,4243,4251,4252,4253,4254,4260,4266,4372,4377,4378,4379,4380,4381,4387,4389,4524,4535,4537,4541,4543,4544,4555,4558,4654,4658,4659,4660,4663,4697,4703,4713,4716,4717,4741,4742,4743,4746,4747,4748,4749,4751,4755,4757,4766,4767,4768,4770,4772,4773,4774,4775,4778,4852,4853,4864,4872,4882],
    "mountain": [20,22,73,76,103,110,120,124,132,138,139,143,144,158,166,199,204,205,208,210,211,222,223,226,330,331,343,344,380,383,384,385,386,388,390,413,414,416,419,422,423,424,426,429,433,434,435,436,448,449,451,452,565,576,577,583,587,676,677,680,689,693,694,697,702,716,718,719,729,732,734,739,783,785,787,791,794,795,797,802,804,807,808,809,810,811,812,813,814,817,820,824,825,827,829,832,856,857,871,872,875,878,879,880,936,974,975,976,977,1048,1066,1078,1180,1210,1213,1214,1223,1246,1273,1768,1831,1850,1853,1871,1873,1952,2003,2020,2073,2103,2104,2105,2107,2108,2111,2112,2117,2125,2127,2130,2136,2154,2155,2169,2177,2178,2179,2180,2181,2186,2189,2190,2196,2198,2201,2204,2205,2206,2207,2210,2211,2212,2217,2218,2220,2221,2222,2223,2225,2226,2234,2236,2305,2306,2327,2332,2345,2346,2371,2381,2395,2396,2444,2467,2468,2470,2477,2480,2481,2484,2485,2486,2491,2493,2494,2495,2505,2506,2564,2604,2605,2609,2610,2612,2613,2615,2617,2743,2760,2761,2769,2791,2813,2817,2824,2825,2826,2827,2828,2829,2831,2835,2836,2837,2839,2843,2845,2862,2871,2872,2873,2874,2877,2940,2941,2942,2947,2982,2990,4054,4060,4128,4131,4158,4171,4175,4198,4201,4205,4206,4210,4211,4214,4215,4216,4217,4222,4232,4236,4268,4280,4281,4282,4296,4300,4301,4302,4303,4304,4306,4310,4326,4329,4330,4331,4332,4335,4338,4339,4340,4342,4344,4345,4348,4404,4481,4482,4514,4515,4516,4517,4518,4519,4520,4521,4546,4568,4582,4601,4602,4611,4631,4632,4634,4641,4643,4645,4647,4648,4653,4655,4656,4679,4680,4681,4682,4693,4710,4722,4727,4733,4734,4740,4750,4754,4758,4759,4783],
    "grasslands": [1,7,13,15,25,26,27,28,33,35,36,39,42,54,55,71,74,75,79,87,89,91,96,114,122,131,135,136,147,149,155,157,159,168,170,171,179,185,202,207,209,213,215,217,218,219,227,229,230,231,237,241,249,265,270,281,292,293,294,295,308,328,373,417,457,458,516,517,526,539,543,549,552,562,572,593,594,597,598,617,618,620,624,626,628,629,630,631,632,635,641,668,703,704,726,730,737,738,741,772,773,778,798,816,819,830,890,891,896,898,901,903,904,905,907,909,952,953,1012,1013,1017,1019,1023,1024,1043,1051,1052,1055,1086,1087,1090,1170,1177,1236,1743,1745,1747,1757,1764,1771,1775,1818,1825,1837,1839,1842,1845,1847,1858,1859,1861,1864,1867,1872,1901,1931,1933,1935,1936,1939,1940,1942,1943,1944,1948,1953,1967,1984,2005,2007,2016,2046,2055,2057,2059,2061,2062,2081,2082,2084,2094,2101,2110,2113,2290,2296,2376,2387,2390,2391,2393,2394,2399,2405,2410,2508,2511,2550,2598,2602,2631,2632,2633,2650,2652,2666,2673,2674,2675,2676,2677,2687,2688,2689,2690,2693,2695,2720,2735,2746,2751,2806,2807,2808,2838,2848,2849,2850,2851,2852,2948,2949,2958,2959,2961,2962,2966,2985,2988,2994,4080,4085,4087,4111,4125,4130,4142,4143,4147,4149,4150,4163,4174,4190,4227,4230,4237,4244,4245,4246,4247,4248,4249,4250,4289,4291,4341,4359,4360,4369,4373,4374,4376,4385,4393,4394,4395,4397,4399,4417,4418,4419,4442,4443,4447,4452,4457,4460,4461,4474,4475,4477,4486,4488,4494,4495,4498,4499,4501,4512,4523,4525,4526,4527,4528,4530,4532,4533,4536,4539,4540,4542,4548,4550,4551,4554,4556,4575,4579,4604,4608,4610,4615,4616,4620,4621,4622,4623,4624,4627,4637,4638,4642,4652,4661,4684,4685,4686,4687,4688,4689,4690,4692,4704,4708,4709,4711,4714,4718,4719,4720,4721,4723,4724,4725,4726,4728,4729,4730,4731,4732,4735,4736,4737,4752,4756,4760,4771,4776,4781,4784,4785,4787,4788,4789,4790,4791,4792,4793,4795,4796,4797,4798,4809,4810,4813,4816,4825,4826,4830,4838,4839,4854,4857,4858,4868,4879,4886,4891,4898,4900,4901,4902,4903,4905,4906,4908,4909,4910,4911,4915,4916,4917,4919,4920],
    "jungle": [486,490,534,535,537,546,547,551,553,560,564,566,567,568,570,571,573,579,580,582,589,590,591,592,595,596,599,601,602,610,616,619,621,622,623,625,627,636,637,638,639,640,660,663,664,666,742,743,744,745,746,747,748,756,757,759,760,761,762,763,764,765,766,769,789,800,801,803,815,818,821,822,826,828,831,835,836,838,840,842,843,845,846,848,1085,1118,1119,1125,1126,1138,1139,1141,1147,1151,1162,1163,1164,1165,1166,1169,1181,1182,1183,1237,1245,1249,1815,1817,1946,2028,2029,2034,2038,2039,2041,2042,2048,2049,2050,2091,2096,2098,2099,2100,2160,2161,2162,2164,2166,2242,2255,2257,2258,2289,2294,2372,2375,2377,2384,2385,2388,2389,2392,2397,2398,2400,2402,2403,2404,2630,2634,2635,2636,2637,2641,2647,2649,2651,2654,2655,2659,2661,2662,2663,2664,2680,2681,2685,2691,2703,2704,2705,2706,2707,2708,2709,2710,2711,2712,2719,2721,2722,2723,2724,2730,2731,2732,2804,2811,2816,2819,2820,2823,2830,2832,2833,2834,2882,2889,2894,2896,2898,2899,2900,2901,2902,2904,2905,2914,2916,2927,2928,2929,2930,2931,2933,2934,2935,2937,2938,2943,2944,2945,2952,4021,4024,4025,4026,4078,4079,4081,4086,4088,4089,4090,4105,4109,4405,4407,4408,4409,4410,4412,4413,4423,4424,4431,4432,4433,4438,4439,4440,4441,4444,4445,4446,4448,4450,4451,4458,4468,4469,4470,4471,4472,4473,4478,4576,4578,4580,4583,4584,4585,4586,4587,4588,4589,4590,4591,4592,4593,4594,4595,4596,4597,4598,4599,4600,4605,4612,4617,4794,4799,4800,4801,4802,4803,4804,4805,4806,4811,4812,4814,4817,4818,4819,4820,4821,4822,4823,4824,4827,4828,4833,4834,4835,4837,4841,4842,4869],
    "marsh": [246,277,278,362,408,462,749,758,775,777,834,893,921,927,928,950,999,1000,1003,1004,1005,1006,1031,1217,1860,1941,2259,2261,2286,2287,2311,2516,2534,2536,2537,2539,2592,2599,2600,2702,2759,2803,2857,2858,2881,2890,2903,4141,4288,4290,4370,4386,4534,4545,4613,4614,4625,4626,4706,4738,4904,4923],
    "desert": [350,352,355,360,391,392,393,403,404,405,409,427,432,437,438,439,440,443,445,447,455,456,465,469,471,477,503,512,513,514,575,698,701,706,707,708,709,710,711,712,715,720,860,861,863,864,867,877,881,1093,1115,1127,1128,1129,1130,1176,1220,1228,1229,1231,1233,1234,1969,1970,2064,2066,2078,2086,2088,2119,2120,2121,2123,2191,2192,2193,2216,2224,2229,2230,2231,2232,2233,2244,2247,2271,2272,2275,2277,2318,2322,2323,2328,2330,2335,2336,2337,2338,2339,2343,2344,2349,2350,2351,2352,2361,2362,2363,2365,2370,2448,2449,2450,2456,2457,2460,2472,2474,2475,2490,2616,2618,2747,2767,2773,2844,2847,2856,2867,4051,4052,4204,4207,4208,4221,4223,4270,4271,4272,4273,4274,4275,4277,4285,4287,4317,4319,4323,4324,4325,4327,4334,4336,4502,4506,4507,4508,4567,4577,4606,4633,4635,4639,4644,4649,4650,4670,4676,4677,4678,4782,4862,4918],
    "coastal_desert": [347,353,354,356,357,364,389,394,395,396,397,398,399,400,401,402,782,792,793,796,805,806,865,866,1099,1111,1112,1174,1206,1209,1212,1215,1230,1232,2024,2315,2320,2321,2324,2325,2326,2329,2331,2333,2340,2341,2342,2347,2451,2452,2726,2765,2786,2788,2789,2790,2793,2821,2822,2840,2841,2954,4269,4278,4283,4284,4286,4847,4848,4849,4865,4866,4867],
    "coastline": [112,126,142,164,233,253,320,333,366,367,368,369,387,481,482,483,487,491,492,493,494,495,496,497,498,499,500,501,502,574,633,634,642,643,644,645,646,647,648,649,650,651,653,654,655,656,659,788,938,957,962,979,982,983,1015,1032,1095,1096,1097,1098,1100,1101,1102,1103,1186,1192,1195,1196,1197,1198,1199,1200,1201,1202,1203,1204,1235,1238,1239,1240,1241,1242,1243,1244,1248,1306,1881,1930,1978,1979,1981,1983,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2002,2348,2547,2554,2561,2578,2678,2679,2683,2684,2686,2692,2696,2699,2700,2713,2714,2716,2717,2718,2725,2728,2741,3003,4020,4049,4193,4279,4349,4350,4351,4352,4353,4354,4355,4356,4364,4365,4559,4560,4565,4651,4698,4700,4745,4815,4934,4935,4936,4937,4938],
    "drylands": [214,220,221,224,225,322,327,334,337,338,341,342,345,377,379,381,382,406,407,411,412,420,421,425,428,430,431,441,442,444,446,450,453,454,464,504,505,519,528,541,569,699,713,750,751,752,753,754,755,786,790,799,858,862,868,876,882,1089,1091,1094,1110,1172,1178,1222,1748,1749,1750,1809,1849,1854,1855,1973,2031,2051,2052,2053,2054,2065,2067,2068,2072,2122,2124,2182,2184,2199,2203,2208,2213,2214,2215,2219,2227,2228,2297,2300,2302,2307,2308,2309,2313,2314,2317,2319,2356,2364,2453,2455,2461,2466,2469,2473,2476,2492,2498,2503,2507,2614,2619,2620,2643,2667,2668,2682,2733,2736,2754,2764,2768,2797,2798,2801,2842,2846,2854,2861,2863,2864,2865,2868,2878,2883,2885,2912,2913,2915,2917,2921,2922,2999,4040,4209,4292,4297,4298,4308,4309,4314,4318,4320,4337,4343,4411,4421,4435,4437,4454,4455,4456,4463,4503,4504,4505,4509,4547,4549,4557,4562,4563,4564,4628,4630,4855,4861,4863],
    "highlands": [23,24,127,145,154,162,163,216,228,252,263,319,321,323,324,326,329,332,335,336,339,340,346,348,349,351,365,370,371,378,418,460,520,536,542,544,578,588,661,662,673,674,675,678,705,736,784,823,850,852,853,869,1047,1171,1184,1185,1188,1207,1208,1211,1218,1219,1224,1227,1247,1318,1751,1766,1773,1846,1882,1968,2006,2018,2019,2035,2077,2079,2085,2087,2093,2131,2132,2133,2134,2135,2165,2167,2168,2170,2183,2202,2209,2235,2274,2298,2301,2303,2401,2454,2458,2459,2462,2463,2464,2465,2478,2483,2488,2489,2496,2501,2504,2621,2622,2623,2624,2626,2628,2629,2644,2645,2646,2734,2748,2752,2755,2756,2757,2758,2762,2763,2766,2770,2771,2772,2778,2779,2781,2787,2792,2946,2950,2951,2960,2968,2986,2989,3001,4027,4029,4030,4053,4055,4056,4057,4059,4067,4073,4077,4084,4100,4101,4103,4110,4199,4228,4238,4293,4294,4295,4299,4305,4313,4391,4398,4406,4422,4436,4464,4553,4561,4566,4669,4699,4701,4780,4859,4860],
    "savannah": [484,485,603,605,606,607,612,614,768,776,870,883,884,887,888,894,897,900,902,913,915,922,923,924,926,929,932,942,1008,1010,1088,1092,1113,1114,1116,1120,1122,1123,1124,1131,1134,1135,1136,1137,1140,1142,1143,1144,1145,1146,1148,1149,1150,1152,1153,1154,1155,1159,1160,1161,1167,1168,1187,1189,1190,1191,1193,1194,1800,1925,2017,2021,2237,2238,2239,2240,2241,2245,2248,2249,2250,2252,2253,2254,2256,2263,2265,2266,2267,2270,2278,2279,2280,2281,2283,2285,2291,2292,2293,2295,2374,2378,2383,2386,2513,2514,2519,2520,2530,2533,2535,2538,2542,2543,2546,2596,2597,2656,2669,2729,2805,2809,2810,2812,2814,2815,2853,2855,2859,2879,2884,2886,2887,2888,2891,2892,2893,2895,2897,2906,2907,2908,2909,2910,2911,2918,2919,2920,2923,2924,2925,2926,2939,4022,4028,4031,4032,4034,4035,4036,4037,4038,4039,4041,4042,4043,4044,4045,4047,4048,4058,4061,4062,4064,4065,4071,4074,4075,4076,4082,4083,4091,4092,4093,4094,4095,4096,4097,4099,4104,4106,4107,4108,4618,4619,4829,4836,4846,4850,4851,4881],
    "steppe": [282,283,284,285,286,287,288,291,299,300,301,302,303,304,459,461,463,466,467,468,470,472,473,474,475,476,478,479,714,717,721,722,723,724,725,728,774,779,780,781,833,885,886,889,892,906,1057,1058,1071,1075,1076,1081,1082,1132,1133,1156,1157,1158,1175,1179,1205,1216,1221,1225,1226,1756,1778,1965,1966,1971,1974,2004,2008,2009,2109,2114,2115,2116,2118,2126,2185,2187,2188,2195,2197,2243,2246,2260,2262,2264,2268,2269,2273,2276,2282,2284,2288,2353,2354,2355,2357,2358,2359,2360,2366,2367,2368,2369,2406,2408,2409,2411,2412,2413,2414,2415,2416,2417,2418,2419,2420,2421,2422,2434,2441,2447,2497,2499,2500,2502,2510,2625,2672,2727,2776,2777,2780,2782,2783,2784,2785,2795,2799,2800,2802,2860,2866,2869,2870,2875,2876,2880,2932,4033,4200,4202,4203,4218,4219,4220,4255,4264,4265,4267,4629,4664,4665,4666,4667,4668,4671,4672,4673,4674,4675,4683],
}
