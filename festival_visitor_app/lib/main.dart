import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const FestivalApp());
}

class FestivalApp extends StatelessWidget {
  const FestivalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: FestivalHomePage(),
    );
  }
}

class FestivalHomePage extends StatefulWidget {
  @override
  State<FestivalHomePage> createState() => _FestivalHomePageState();
}

class _FestivalHomePageState extends State<FestivalHomePage> {
  List zones = [];
  Timer? refreshTimer;

  final String apiUrl =
      "http://192.168.1.196:5000/zone-status"; //macbook lokale API

  @override
  void initState() {
    super.initState();
    fetchZones();

    refreshTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      fetchZones();
    });
  }

  @override
  void dispose() {
    refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> fetchZones() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        setState(() {
          zones = json.decode(response.body);
        });
      }
    } catch (e) {
      print(e);
    }
  }

  Color getZoneColor(String density) {
    if (density == "HIGH") {
      return const Color.fromARGB(255, 241, 51, 44);
    } else if (density == "MEDIUM") {
      return const Color.fromARGB(255, 255, 135, 6);
    }
    return const Color.fromARGB(255, 77, 212, 81);
  }

  String getDensity(String zoneName) {
    try {
      return zones.firstWhere((z) => z["Name"] == zoneName)["DensityLevel"];
    } catch (e) {
      return "LOW";
    }
  }

  Widget buildHeatZone({
    required double top,
    required double left,
    required double size,
    required String zoneName,
  }) {
    Color baseColor = getZoneColor(getDensity(zoneName));

    double pulseMultiplier = 1.0;
    String density = getDensity(zoneName);

    if (density == "HIGH") {
      pulseMultiplier = 1.18;
    } else if (density == "MEDIUM") {
      pulseMultiplier = 1.10;
    }

    return Positioned(
      top: top,
      left: left,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.95, end: pulseMultiplier),
        duration: const Duration(milliseconds: 1800),
        curve: Curves.easeInOut,
        builder: (context, scale, child) {
          return Transform.scale(
            scale: scale,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  width: size * 0.1,
                  height: size * 0.1,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: baseColor.withOpacity(0.25),
                        blurRadius: 40,
                        spreadRadius: 16,
                      ),
                    ],
                  ),
                ),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 1200),
                  width: size,
                  height: size,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      stops: const [0.0, 0.18, 0.38, 0.65, 1.0],
                      colors: [
                        baseColor.withOpacity(1.0),
                        baseColor.withOpacity(0.92),
                        baseColor.withOpacity(0.70),
                        baseColor.withOpacity(0.38),
                        Colors.transparent,
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: baseColor.withOpacity(0.55),
                        blurRadius: 60,
                        spreadRadius: 25,
                      ),
                      BoxShadow(
                        color: baseColor.withOpacity(0.25),
                        blurRadius: 90,
                        spreadRadius: 30,
                      ),
                    ],
                  ),
                ),
                Container(
                  width: size * 0.25,
                  height: size * 0.25,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withOpacity(0.25),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7E7E2),
      body: SafeArea(
        child: Column(
          children: [
            // MAP
            Expanded(
              child: Stack(
                children: [
                  Positioned.fill(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(30),
                        child: Image.asset(
                          "assets/festival_map.jpg",
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  ),

                  // LIVE HEATMAP ZONES
                  buildHeatZone(
                    top: 70,
                    left: 200,
                    size: 130,

                    zoneName: "MainStage",
                  ),

                  buildHeatZone(
                    top: 200,
                    left: 20,
                    size: 80,

                    zoneName: "Entrance",
                  ),

                  buildHeatZone(
                    top: 120,
                    left: 170,
                    size: 50,

                    zoneName: "FoodCourt",
                  ),

                  buildHeatZone(
                    top: 170,
                    left: 260,
                    size: 80,

                    zoneName: "ChillZone",
                  ),

                  buildHeatZone(
                    top: 280,
                    left: 130,
                    size: 80,

                    zoneName: "Amapiano Stage",
                  ),

                  buildHeatZone(
                    top: 120,
                    left: 100,
                    size: 80,

                    zoneName: "Dancehall Stage",
                  ),

                  buildHeatZone(
                    top: 290,
                    left: 210,
                    size: 70,

                    zoneName: "HipHop Stage",
                  ),

                  buildHeatZone(
                    top: 250,
                    left: 200,
                    size: 60,

                    zoneName: "Notes Stage",
                  ),

                  buildHeatZone(
                    top: 175,
                    left: 140,
                    size: 60,

                    zoneName: "Spotlight Stage",
                  ),

                  buildHeatZone(
                    top: 240,
                    left: 250,
                    size: 50,

                    zoneName: "FoodCourt South",
                  ),

                  buildHeatZone(
                    top: 260,
                    left: 130,
                    size: 50,

                    zoneName: "Toilets West",
                  ),

                  buildHeatZone(
                    top: 210,
                    left: 190,
                    size: 50,

                    zoneName: "Toilets East",
                  ),

                  //OVERLAY IMAGE
                  Positioned(
                    top: 3,
                    left: -95,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/amastage.png"),
                  ),
                  //OVERLAY IMAGE
                  Positioned(
                    top: 3,
                    left: -103,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/chillzone.png"),
                  ),

                  Positioned(
                    top: 4,
                    left: -95,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/dancehall.png"),
                  ),
                  Positioned(
                    top: 1,
                    left: -101,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/foodcourtbottom.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/foodcourtup.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/hiphopstage.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/mainstage.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/notesstage.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/spotlightstage.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/wcbottom.png"),
                  ),
                  Positioned(
                    top: 5,
                    left: -100,
                    width: 600,
                    height: 600,
                    child: Image.asset("assets/wcmidden.png"),
                  ),

                  //

                  // REFRESH BUTTON
                  Positioned(
                    top: 30,
                    right: 30,
                    child: FloatingActionButton(
                      backgroundColor: Colors.white,
                      onPressed: fetchZones,
                      child: const Icon(Icons.refresh, color: Colors.black),
                    ),
                  ),

                  // LEGEND
                  Positioned(
                    bottom: 50,
                    left: 30,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 6,
                              backgroundColor: Colors.green,
                            ),
                            SizedBox(width: 8),
                            Text(
                              "Rustig",
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 8),
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 6,
                              backgroundColor: Colors.orange,
                            ),
                            SizedBox(width: 8),
                            Text(
                              "Druk",
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 8),
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 6,
                              backgroundColor: Colors.red,
                            ),
                            SizedBox(width: 8),
                            Text(
                              "Te druk",
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            // BOTTOM PANEL
            Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        showDialog(
                          context: context,
                          builder: (context) {
                            return AlertDialog(
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(24),
                              ),
                              title: const Text("🚨 Distress Message"),
                              content: const Text(
                                "Next step:\n\nConnect this form to your API.",
                              ),
                            );
                          },
                        );
                      },
                      child: Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(28),
                          border: Border.all(
                            color: Colors.red.shade900,
                            width: 2,
                          ),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.warning_rounded,
                              color: Colors.red,
                              size: 50,
                            ),
                            SizedBox(width: 18),
                            Text(
                              "Meld een\nprobleem",
                              style: TextStyle(fontSize: 22),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
