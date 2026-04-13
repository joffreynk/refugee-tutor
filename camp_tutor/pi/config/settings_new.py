"""Configuration settings for Camp Tutor robot."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

HOSTNAME = "refugeetutor"
WEB_PORT = 5000
WEB_URL = f"http://{HOSTNAME}:{WEB_PORT}/"
WEB_SECRET_KEY = os.environ.get("WEB_SECRET_KEY", "camp-tutor-secret-key")

I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_ADDRESS = 0x42
I2C_SPEED_HZ = 100000

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 1024
AUDIO_BUFFER_SIZE = 4096
AUDIO_MAX_DISTANCE = 500
AUDIO_NOISE_THRESHOLD = 0.02
AUDIO_NOISE_GATE_MS = 100
AUDIO_VOICE_ACTIVATION_THRESHOLD = 0.015
AUDIO_MIN_SNR_DB = 10
AUDIO_HIGH_PASS_FILTER_HZ = 80
AUDIO_LOW_PASS_FILTER_HZ = 8000
DEFAULT_VOLUME = 0.5
DEFAULT_SPEECH_RATE = 90
DEFAULT_LANGUAGE = "en"

WAKE_WORD = "hello tutor robot"
WAKE_THRESHOLD = 0.5
INACTIVITY_TIMEOUT = 300

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FRAMERATE = 15

LCD_WIDTH = 84
LCD_HEIGHT = 48
LCD_CONTRAST = 0xBF
LCD_BIAS = 0x04

REX_LOOK_ANGLES = {
    "LEFT": (90, 45),
    "CENTER": (0, 30),
    "RIGHT": (-90, 45),
}

LANGUAGE_CODES = ["en", "zh", "fr", "de", "es", "it", "pt", "ar", "hi", "ru"]
LANGUAGE_NAMES = {
    "en": "English", "zh": "Chinese", "fr": "French", "de": "German",
    "es": "Spanish", "it": "Italian", "pt": "Portuguese", "ar": "Arabic",
    "hi": "Hindi", "ru": "Russian"
}

AGE_GROUPS = {
    "early": {"name": "Early Years", "min": 3, "max": 5},
    "primary": {"name": "Primary", "min": 5, "max": 11},
    "lower_secondary": {"name": "Lower Secondary", "min": 11, "max": 14},
    "upper_secondary": {"name": "Upper Secondary", "min": 14, "max": 18},
}

CURRICULUM_SUBJECTS = ["mathematics", "science", "english", "global_citizenship", "computing", "programming"]

COMPREHENSIVE_CURRICULUM = {
    "early": {
        "mathematics": {
            "topics": [
                {"name": "Numbers", "subtopics": ["counting", "ordering", "matching", "more_less", "adding", "subtracting", "sharing", "patterns", "size", "money"]},
                {"name": "Shapes", "subtopics": ["circles", "squares", "triangles", "colour", "size", "sorting", "patterns", "position", "symmetry", "3d"]},
                {"name": "Measurement", "subtopics": ["length", "weight", "time", "money", "capacity", "temperature", "comparing", "ordering", "estimating", "non_standard"]},
                {"name": "Patterns", "subtopics": ["colour_patterns", "shape_patterns", "number_patterns", "growing_patterns", "sharing_equally", "created_patterns", "continue_pattern", "missing_pattern", "describe_pattern", "create_rule"]},
                {"name": "Problem Solving", "subtopics": ["counting_strategies", "trial_improvement", "use_equipment", "logical_thinking", "act_it_out", "draw_diagram", "work_systematically", "check_answers", "explain_reasoning", "different_ways"]},
                {"name": "Position", "subtopics": ["top_bottom", "inside_outside", "front_back", "next_to", "over_under", "direction", "map_reading", "give_directions", "describe_position", "follow_route"]},
                {"name": "Time", "subtopics": ["day_night", "days_week", "months_year", "o_clock", "half_past", "quarter_past", "quarter_to", "tell_time", "duration", "time_intervals"]},
                {"name": "Data", "subtopics": ["sorting", "collecting", "recording", "pictures", "tally", "bar_chart", "interpret", "question", "tally_chart", "simple_graph"]},
                {"name": "Money", "subtopics": ["recognise_coins", "recognise_notes", "counting_coins", "making_amount", "pence_pounds", "change", "spending", "saving", "prices", "value_money"]},
                {"name": "Addition", "subtopics": ["count_on", "number_bonds", "doubles", "near_doubles", "missing_numbers", "add_tens", "add_teen", "commutative", "inverse", "word_problems"]}
            ]
        },
        "english": {
            "topics": [
                {"name": "Phonics", "subtopics": ["s_sounds", "m_sounds", "a_sounds", "t_sounds", "d_sounds", "n_sounds", "i_sounds", "p_sounds", "o_sounds", "g_sounds"]},
                {"name": "Speaking", "subtopics": ["share_ideas", "listen_others", "take_turns", "ask_questions", "answer_questions", "retell_story", "describe_things", "use_words", "sentence_talk", "talk_loudly"]},
                {"name": "Listening", "subtopics": ["listen_carefully", "hear_sounds", "follow_instructions", "story_listening", "rhythm_rhymes", "sounds_words", "complete_sentence", "remember_details", "respond_appropriately", "active_listening"]},
                {"name": "Reading", "subtopics": ["look_at_books", "name_letters", "read_words", "simple_books", "picture_clues", "blend_cvc", "read_sentences", "re_read", "independent", "reading_choices"]},
                {"name": "Writing", "subtopics": ["mark_make", "write_letters", "write_name", "draw_pictures", "label_things", "write_cvc", "write_sentences", "begin_sentence", "full_stops", "finger_spaces"]},
                {"name": "Captions", "subtopics": ["labels", "captions_photos", "match_word", "simple_caption", "caption_sentence", "add_detail", "caption_picture", "caption_character", "caption_scene", "caption_story"]},
                {"name": "Stories", "subtopics": ["retell_story", "story_words", "story_sequence", "story_characters", "story_settings", "own_story", "story_ending", "illustrate_story", "read_story", "story_map"]},
                {"name": "Rhymes", "subtopics": ["rhyming_words", "listen_rhymes", "repeat_rhymes", "rhythm", "rhyming_pairs", "create_rhyme", "rhyme_game", "rhyming_pattern", "action_rhymes", "performance_rhymes"]},
                {"name": "Vocabulary", "subtopics": ["new_words", "word_meaning", "use_words", "describe", "word_wall", "word_of_day", "word_class", "rich_vocabulary", "word_families", "word_webs"]},
                {"name": "Spelling", "subtopics": ["s_letter", "t_letter", "a_letter", "name_spelling", "high_frequency", "sound_spelling", "tricky_words", "segmenting", "spelling_rules", "correct_spelling", "practice_words"]}
            ]
        },
        "science": {
            "topics": [
                {"name": "Our Bodies", "subtopics": ["body_parts", "senses", "healthy_eating", "exercise", "rest", "hygiene", "food_groups", "teeth", "growth", "bones_muscles"]},
                {"name": "Animals", "subtopics": ["pet_animals", "wild_animals", "baby_animals", "animal_homes", "food_animals", "animal_covering", "how_move", "how_sound", "animal_bodies", "life_cycles"]},
                {"name": "Plants", "subtopics": ["plant_parts", "planting_seeds", "needs_plants", "water_plants", "sunlight", "plant_growth", "leaves", "flowers", "from_seed", "planting_activities"]},
                {"name": "Materials", "subtopics": ["hard_soft", "rough_smooth", "bouncy", "waterproof", "absorbent", "flexible", "transparent", "magnetic", "float_sink", "changes"]},
                {"name": "Weather", "subtopics": ["sunny_weather", "rainy_weather", "windy", "cloudy", "snowy", "weather_signs", "daily_weather", "weather_chart", "seasonal_weather", "weather_differences"]},
                {"name": "Light", "subtopics": ["light_dark", "light_sources", "shadows", "shadow_changing", "bright_dark", "reflection", "see_things", "how_light", "reflective", "natural_light"]},
                {"name": "Sound", "subtopics": ["loud_quiet", "high_low", "vibrations", "sounds_near", "sounds_far", "make_sounds", "sound_sources", "hearing_sounds", "quiet_sounds", "sound_patterns"]},
                {"name": "Floating", "subtopics": ["float_sink", "water_displacement", "upthrust", "density", "shape_float", " buoyancy", "explain_floating", "floating_objects", "sink_floating", "predictions_floating"]},
                {"name": "Push_Pull", "subtopics": ["push", "pull", "pushes_pulls", "direction", "strength", "movement", "stop_movement", "force", "balanced", "unbalanced"]},
                {"name": "Magnets", "subtopics": ["magnetic", "non_magnetic", "attraction", "magnet_poles", "magnetic_forces", "magnetic_field", "magnetic_objects", "does_work", "magnet_strength", "magnet_uses"]}
            ]
        }
    },
    "primary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["place_value", "addition", "subtraction", "multiplication", "division", "fractions", "decimals", "negative_numbers", "rounding", "estimation"]},
                {"name": "Geometry", "subtopics": ["2d_shapes", "3d_shapes", "angles", "symmetry", "coordinates", "transformations", "perimeter", "area", "lines", "reflection"]},
                {"name": "Measurement", "subtopics": ["length", "mass", "time", "money", "area", "perimeter", "volume", "temperature", "conversion", "capacity"]},
                {"name": "Statistics", "subtopics": ["bar_charts", "pictograms", "tally", "tables", "graphs", "averages", "mode", "range", "interpretation", "questions"]},
                {"name": "Algebra", "subtopics": ["sequences", "input_output", "equations", "formulae", "functions", "patterns", "inverse", "substitution", "solving", "graphs"]},
                {"name": "Fractions", "subtopics": ["equivalent", "ordering", "addition", "subtraction", "multiplication", "division", "mixed_numbers", "simplifying", "percentage", "decimal_fractions"]},
                {"name": "Ratio", "subtopics": ["ratio_language", "simplify_ratio", "share_ratio", "scale_drawing", "map_scales", "ratio_problems", "double", "half", "ratio_tables", "three_part_ratio"]},
                {"name": "Percentages", "subtopics": ["percentage_of", "percentage_increase", "percentage_decrease", "percentage_change", "percentage_multipliers", "reverse_percentages", "percentage_problems", "interest", "discount", "profit_loss"]},
                {"name": "Angles", "subtopics": ["angle_sizes", "angle_rules", "vertically_opposite", "angles_triangle", "angles_quadrilateral", "angles_polygon", "bearings", "constructions", "angle_chase", "angle_probs"]},
                {"name": "Decimals", "subtopics": ["place_value", "addition", "subtraction", "multiplication", "division", "rounding", "estimation", "equivalence", "order_decimals", "four_operations"]}
            ]
        },
        "english": {
            "topics": [
                {"name": "Reading", "subtopics": ["comprehension", "vocabulary", "inference", "genres", "poetry", "non_fiction", "fiction", "newspapers", "digital_texts", "summarising"]},
                {"name": "Writing", "subtopics": ["narrative", "description", "instructions", "letters", "reports", "persuasion", "dialogue", "paragraphs", "editing", "publishing"]},
                {"name": "Grammar", "subtopics": ["punctuation", "spelling", "connectives", "tense", "paragraphs", "adjectives", "adverbs", "pronouns", "conjunctions", "prepositions"]},
                {"name": "Speaking", "subtopics": ["dialogue", "presentation", "drama", "debate", "recitation", "conversation", "discussion", "listening", "performing", "interviewing"]},
                {"name": "Spelling", "subtopics": ["common_words", "patterns", "rules", "homophones", "prefixes", "suffixes", "silent_letters", "double_letters", "word_families", "anagrams"]},
                {"name": "Punctuation", "subtopics": ["full_stops", "commas", "question_marks", "exclamation", "apostrophes", "quotation_marks", "colons_semicolons", "hyphens", "parentheses", "brackets"]},
                {"name": "Vocabulary", "subtopics": ["synonyms", "antonyms", "word_choice", "word_building", "word_roots", "word_prefixes", "word_suffixes", "idioms", "collocation", "abstract_words"]},
                {"name": "Shakespeare", "subtopics": ["biography", "plays", "characters", "themes_language", "historical_context", "modern_adaptations", "language_structures", "theatrical_conventions", " Globe_theatre", "performance"]},
                {"name": "Poetry", "subtopics": ["structural_features", "language_imagery", "metaphor", "simile", "personification", "alliteration", "rhythm_rhyme", "concrete_poems", "free_verse", "response_poems"]},
                {"name": "Analysis", "subtopics": ["author_purpose", " viewpoint", "persuasive_techniques", "text_structure", "language_choice", "evaluating_texts", "comparing_texts", "analytical_writing", "critical_view", "personal_response"]}
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells", "humans", "animals", "plants", "ecosystems", "food_chains", "variation", "inheritance", "reproduction", "classification"]},
                {"name": "Chemistry", "subtopics": ["materials", "states", "changes", "mixtures", "acids", "properties", "reactions", "elements", "compounds", "periodic"]},
                {"name": "Physics", "subtopics": ["forces", "motion", "energy", "light", "sound", "electricity", "magnets", "waves", "pressure", "simple_machines"]},
                {"name": "Earth", "subtopics": ["rocks", "fossils", "weather", "climate", "solar_system", "earth_moon", "erosion", "volcanoes", "earthquakes", "resources"]},
                {"name": "Method", "subtopics": ["hypotheses", "experiments", "evidence", "analysis", "conclusions", "fair_testing", "variables", "measurement", "recording", "reporting"]},
                {"name": "Forces", "subtopics": ["contact_forces", "non_contact", "gravity", "friction", "air_resistance", "elastic", "moments", "pressure", "vectors", "Newton"]},
                {"name": "Light", "subtopics": ["straight_lines", "reflection", "refraction", "lenses", "colour", "shadows", "rays", "images", "speed_light", "electromagnetic"]},
                {"name": "Electricity", "subtopics": ["circuits", "current", "voltage", "resistance", "series_parallel", "static", "electric_fields", "power", "efficiency", "magnetism"]},
                {"name": "Evolution", "subtopics": ["inheritance", "variation", "adaptation", "natural_selection", "evolutionary_relationships", "fossils", "genetics", "selective_breeding", "evidence_evolution", "human_evolution"]},
                {"name": "Ecosystems", "subtopics": [" interdependence", "energy_flow", "nutrient_cycling", "habitats", "food_webs", "population", "environmental_change", "biodiversity", "conservation", "sustainability"]}
            ]
        },
        "computing": {
            "topics": [
                {"name": "Digital", "subtopics": ["devices", "software", "files", "internet_safety", "keyboarding", "coding", "email", "passwords", "searching", "digital_footprint"]},
                {"name": "Algorithms", "subtopics": ["sequences", "loops", "conditions", "variables", "debugging", "designing", "flowcharts", "pseudocode", "bubble_sort", "binary_search"]},
                {"name": "Networks", "subtopics": ["network_types", "internet", "IP_addresses", "DNS", "protocols", "routers", "switches", "firewalls", "wireless", "web_browsing", "web_servers"]},
                {"name": "Data", "subtopics": ["binary", "hexadecimal", "ASCII", "Unicode", "images", "sound", "compression", "encryption", "databases", "SQL", "storage"]},
                {"name": "Programming", "subtopics": ["algorithms", "pseudocode", "variables", "data_types", "selection", "iteration", "subroutines", "files", "error_handling", "testing"]},
                {"name": "Hardware", "subtopics": ["CPU", "memory", "storage", "input", "output", "motherboard", "buses", "binary_logic", "logic_gates", "microcontrollers"]},
                {"name": "Software", "subtopics": ["systems_software", "application_software", "utilities", "licensing", "updates", "virtualisation", "operating_systems", "device_drivers", "firmware", "middleware"]},
                {"name": "Security", "subtopics": ["malware", "phishing", "authentication", "encryption", "backup", "firewalls", "updates", "password_security", "network_security", "social_engineering"]},
                {"name": "Logic", "subtopics": ["boolean", "AND_OR_NOT", "logic_circuits", "truth_tables", "gate_symbols", "NAND_NOR", "De_Morgan", "simplification", "K_maps", "sequencing"]},
                {"name": "Impact", "subtopics": ["digital_divide", "accessibility", "ethics", "privacy", "environmental", "employment", "cybercrime", "digital_citizenship", "addiction", "communication"]}
            ]
        }
    },
    "lower_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["integers", "fractions", "decimals", "percentages", "ratios", "bounds", "standard_form", "surds", "recurring", "estimation"]},
                {"name": "Algebra", "subtopics": ["expressions", "equations", "inequalities", "graphs", "sequences", "formulae", "functions", "rearranging", "factorising", "completing"]},
                {"name": "Geometry", "subtopics": ["angles", "polygons", "circles", "congruence", "Pythagoras", "trigonometry", "vectors", "transformations", "constructions", "loci"]},
                {"name": "Statistics", "subtopics": ["collection", "representation", "averages", "spread", "probability", "hypothesis", "correlation", "sampling", "bias", "frequency"]},
                {"name": "Advanced", "subtopics": ["indices", "roots", "factors", "multiples", "primes", "modular", "sequences", "series", "proof", "number_theory"]},
                {"name": "Graphs", "subtopics": ["straight_line", "quadratic", "cubic", "reciprocal", "exponential", "trigonometric", "real_life", "gradient", "equation_lines", "intersection"]},
                {"name": "Trigonometry", "subtopics": ["sine", "cosine", "tangent", "trig_graphs", "angles_90", "trig_equations", "area_formula", "ambiguous_case", "3d_trig", "bearing_trig"]},
                {"name": "Vectors", "subtopics": ["magnitude_direction", "component_form", "addition", "scalar_multiplication", "position_vectors", "vector_equation", "parallel_perpendicular", "collinear", "midpoint", "applications"]},
                {"name": "Circles", "subtopics": ["circle_theorem", "tangent_theorem", "chord_theorem", "angle_theorem", "circumference", "area_circle", "sector_area", "segment_area", "arc_length", "circle_equations"]},
                {"name": "Proof", "subtopics": ["direct_proof", "indirect", "proof_by_contradiction", "exhaustion", "counter_example", "generic_proof", "algebraic_proof", "geometric_proof", "number_proof", "sequence_proof", "inequality_proof"]}
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["novels", "poetry", "drama", "analysis", "themes", "context", "characters", "plot", "setting", "comparison"]},
                {"name": "Language", "subtopics": ["grammar", "vocabulary", "usage", "orthography", "discourse", "register", "pragmatics", "sociolinguistics", "idiolect", "dialect"]},
                {"name": "Creative", "subtopics": ["narrative", "description", "dialogue", "style", "voice", "revision", "feedback", "publication", "genre", "structure"]},
                {"name": "Media", "subtopics": ["analysis", "representation", "bias", "techniques", "production", "audience", "industry", "regulation", "convergence", "digital"]},
                {"name": "Communication", "subtopics": ["speaking", "listening", "discussion", "debate", "presentation", "interview", "rhetoric", "persuasion", "negotiation", "collaboration"]},
                {"name": "Transactional", "subtopics": ["letters", "emails", "speeches", "proposals", "reviews", "articles", "leaflets", "advertisements", "campaigns", "publications"]},
                {"name": "Analysis", "subtopics": ["close_reading", "language_analysis", "structural_analysis", "comparative_analysis", "contextual_analysis", "critical_literacy", "theoretical_lens", "representations", "ideology", "intertextuality"]},
                {"name": "Creative_Non_Fiction", "subtopics": ["travel_writing", "autobiography", "biography", "memoir", "personal_essay", "journalism", "food_writing", "nature_writing", "science_writing", "cultural_commentary"]},
                {"name": "Spoken", "subtopics": ["formal_presentation", "impromptu", "dramatic_performance", "structured_debate", "speech", "interview_techniques", "storytelling", "spoken_poetry", "commentary", "persuasive_speaking"]},
                {"name": "Theory", "subtopics": ["narratology", "stylistics", "discourse_theory", "genre_theory", "feminist_criticism", "postcolonial_theory", "marxist_criticism", "psychoanalytic_criticism", "reader_response", "cultural_theory"]}
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells", "organisation", "nutrition", "digestion", "transport", "bioenergetics", "homeostasis", "inheritance", "variation", "ecosystems"]},
                {"name": "Chemistry", "subtopics": ["particles", "elements", "compounds", "mixtures", "reactions", "energy", "periodic", "acids", "extraction", "analytical"]},
                {"name": "Physics", "subtopics": ["forces", "motion", "Newton", "energy", "waves", "electricity", "magnetism", "matter", "radioactivity", "space"]},
                {"name": "Earth", "subtopics": ["atmosphere", "hydrosphere", "lithosphere", "climate", "sustainable", "carbon", "water_cycle", "weather", "oceanography", "geological"]},
                {"name": "Practical", "subtopics": ["measurement", "variables", "accuracy", "precision", "analysis", "evaluation", "report", "graph_drawing", "calculations", "uncertainty"]},
                {"name": "Genetics", "subtopics": ["DNA", "genes", "alleles", "punnett_squares", "inheritance_patterns", "variation", "genetic_conditions", "cloning", "gene_technology", "ethical_debates"]},
                {"name": "Forces", "subtopics": ["resultant_forces", "resolution", "friction", "drag", "terminal_velocity", "circular_motion", "simple_harmonic", "projectiles", "oscillations", "damped"]},
                {"name": "Waves", "subtopics": ["wave_equation", "reflection", "refraction", "diffraction", "interference", "standing_waves", "Doppler", "EM_spectrum", "lenses", "optical_instruments"]},
                {"name": "Energy", "subtopics": ["energy_stores", "energy_changes", "work_power", "energy_efficiency", "heat_engines", "thermal_conductivity", "specific_heat", "latent_heat", "energy_resources", "energy_environment"]},
                {"name": "Fields", "subtopics": ["gravitational_fields", "electric_fields", "magnetic_fields", "field_strength", "field_lines", "potential", "point_masses", "Coulomb", "electromagnetic", "field_patterns"]}
            ]
        },
        "computing": {
            "topics": [
                {"name": "Systems", "subtopics": ["hardware", "software", "networks", "data", "binary", "storage", "compression", "encryption", "databases", "OS"]},
                {"name": "Algorithms", "subtopics": ["designing", "efficiency", "searching", "sorting", "pseudo", "flowcharts", "bubble", "merge", "binary_search", "big_O"]},
                {"name": "Programming", "subtopics": ["syntax", "variables", "data_types", "control", "functions", "arrays", "files", "error_handling", "OOP", "debugging"]},
                {"name": "Data", "subtopics": ["arrays", "lists", "stacks", "queues", "trees", "graphs", "hash_tables", "implementations", "applications", "big_data"]},
                {"name": "Ethics", "subtopics": ["IP", "plagiarism", "licensing", "privacy", "data_protection", "security", "ethical_hacking", "AI_ethics", "digital_wellbeing", "environment", "accessibility"]},
                {"name": "Networks", "subtopics": ["network_layers", "topology", "protocols", "packet_switching", "routing", "firewalls", "proxy", "DNS", "DHCP", "network_security"]},
                {"name": "Databases", "subtopics": ["ER_diagrams", " normalisation", "SQL_queries", "joins", "aggregation", "subqueries", "views", "indexes", "transactions", "ACID", "NoSQL"]},
                {"name": "Web", "subtopics": ["HTTP", "HTML_CSS", "JavaScript", "backend", "REST_API", "authentication", "security", "performance", "SEO", "accessibility"]},
                {"name": "Software", "subtopics": ["SDLC", "agile", "waterfall", "testing_levels", "test_driven", "continuous_integration", "deployment", "maintenance", "documentation", "version_control"]},
                {"name": "Computing", "subtopics": ["automata", "computability", "complexity", "tractability", "NP_problems", "Turing_test", "AI_history", "machine_learning", "robotics", "future_computing"]}
            ]
        }
    },
    "upper_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Pure", "subtopics": ["algebra", "calculus", "trigonometry", "sequences", "series", "vectors", "complex", "matrices", "proof_induction", "functions"]},
                {"name": "Mechanics", "subtopics": ["kinematics", "forces", "Newton", "moments", "energy", "power", "momentum", "circular", "projectiles", "Hook"]},
                {"name": "Statistics", "subtopics": ["probability", "distributions", "hypothesis", "correlation", "regression", "normal", "confidence", "binomial", "contingency", "type_errors"]},
                {"name": "Decision", "subtopics": ["algorithms", "graphs", "linear_programming", "networks", "critical_path", "allocation", "route_inspection", "matching", "flow", "dynamic"]},
                {"name": "Calculus", "subtopics": ["differentiation", "integration", "differential", "Taylor", "numerical", "parametric", "implicit", "related_rates", "areas", "mean_value"]},
                {"name": "Complex", "subtopics": ["complex_plane", "modulus_argument", "polar_form", "De_Moivre", "roots_unity", "exponential_form", "geometrical_interpretation", "loci", "mapping", "transformations"]},
                {"name": "Matrices", "subtopics": ["matrix_operations", "determinants", "inverse_matrices", "simultaneous", "transformations", "eigenvalues", "eigenvectors", "markov_chains", "CRT", "matrix_properties"]},
                {"name": "Series", "subtopics": ["arithmetic_geometric", "infinite_series", "binomial_series", "Maclaurin", "Taylor_series", "convergence_tests", "ratio_test", "root_test", "alternating", "remainder"]},
                {"name": "Statistics", "subtopics": ["geometric", "Poisson", "exponential", "continuous_random", "hypothesis", "chi_squared", "t_test", "confidence", "ANOVA", "significance"]},
                {"name": "Proof", "subtopics": ["proof_by_induction", "contradiction", "contraposition", "exhaustion", "counter_example", "direct_proof", "existence", "uniqueness", "constructive", "axiom_based"]}
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["Shakespeare", "poetry", "prose", "drama", "theory", "context", "genre", "narrative_voice", "symbolism", "comparative"]},
                {"name": "Language", "subtopics": ["dialect", "variation", "register", "pragmatics", "discourse", "history", "orthography", "standard_English", "global_English", "social"]},
                {"name": "Creative", "subtopics": ["fiction", "non_fiction", "poetry", "drama_script", "reflection", "publication", "workshop", "beta_reading", "experimental", "professional"]},
                {"name": "Rhetoric", "subtopics": ["argument", "devices", "sophistry", "audience", "ethos", "propaganda", "spin", "counter", "debate", "oratory"]},
                {"name": "Media", "subtopics": ["theory", "film", "audience_theory", "representation", "ownership", "convergence", "transmedia", "global", "regulation", "platform"]},
                {"name": "Shakespeare", "subtopics": ["plays_histories", "comedies", "tragedies", "late_plays", "language", "staging", "characters", "themes", "sources", "criticism"]},
                {"name": "Poetry", "subtopics": ["Romantic", "Victorian", "modern", "war_poetry", "American_poetry", "postcolonial_poetry", "poetry_analysis", "comparative_poetry", "performance_poetry", "creative_responses"]},
                {"name": "Prose", "subtopics": ["novel_study", "short_stories", "non_fiction_prose", "autobiography", "biography", "historical_fiction", "science_fiction", "Gothic", "realist", "modernist"]},
                {"name": "Theory", "subtopics": ["feminist", "marxist", "psychoanalytic", "postcolonial", "poststructuralist", "queer", "new_historicist", "ethical", "ecocritical", "disability_studies"]},
                {"name": "Cognition", "subtopics": ["reading_cognition", "writing_cognition", "memory_studies", "comprehension", "critical_thinking", "creativity", "decision_making", "problem_solving", "empathy", "communication_skills"]}
            ]
        },
        "science": {
            "topics": [
                {"name": "Physics", "subtopics": ["mechanics", "fields", "gravitational", "electric", "magnetic", "induction", "wave_particles", "thermal", "nuclear", "cosmology"]},
                {"name": "Chemistry", "subtopics": ["organic", "mechanisms", "stereochemistry", "carbonyl", "amines", "polymers", "spectroscopy", "thermodynamics", "electrochemistry", "analytical"]},
                {"name": "Biology", "subtopics": ["cell", "biochemistry", "genetics", "molecular", "ecology", "evolution", "physiology", "immune", "bioinformatics", "systems"]},
                {"name": "Environmental", "subtopics": ["pollution", "conservation", "climate", "renewable", "sustainability", "biodiversity", "resource", "waste", "carbon_footprint", "impact", "management"]},
                {"name": "Research", "subtopics": ["methodology", "statistics", "sampling", "qualitative", "quantitative", "peer_review", "replication", "meta", "ethics", "communication"]},
                {"name": "Quantum", "subtopics": ["wave_particles", "Heisenberg", "Schrodinger", "quantum_numbers", "orbitals", "tunnelling", "uncertainty", "spin", "entanglement", "quantum_computing"]},
                {"name": "Relativity", "subtopics": ["time_dilation", "length_contraction", "mass_energy", "equivalence", "spacetime", "general_relativity", "gravitational_lensing", "black_holes", "GPS", "cosmology"]},
                {"name": "Genetics", "subtopics": ["DNA_structure", "gene_expression", "epigenetics", "genetic_engineering", "CRISPR", "personalised_medicine", "pharmacogenomics", "genetic_counselling", "forensic_genetics", "synthetic_biology"]},
                {"name": "Neuroscience", "subtopics": ["brain_structure", "neurones", "synapses", "neurotransmitters", "brain_imaging", "consciousness", "learning", "memory", "emotion", "disorders", "treatments"]},
                {"name": "Astronomy", "subtopics": ["stellar_evolution", "galaxies", "cosmic_scale", "exoplanets", "dark_matter", "dark_energy", "cosmology", "observation", "telescopes", "space_exploration"]}
            ]
        },
        "computing": {
            "topics": [
                {"name": "Systems", "subtopics": ["architecture", "networks", "OS", "databases", "security", "virtualisation", "cloud", "distributed", "performance", "management"]},
                {"name": "Algorithms", "subtopics": ["time_complexity", "space", "sorting", "searching", "graphs", "dynamic", "greedy", "divide_conquer", "string", "crypto"]},
                {"name": "Programming", "subtopics": ["OOP", "patterns", "testing", "documentation", "debugging", "version_control", "refactoring", "SOLID", "DI", "CI_CD"]},
                {"name": "Data", "subtopics": ["structures", "compression", "encryption", "SQL", "NoSQL", "transactions", "ACID", "Big_Data", "warehousing", "lakes"]},
                {"name": "Web", "subtopics": ["HTML5", "CSS3", "JavaScript", "backend", "REST", "GraphQL", "authentication", "security", "performance", "PWA"]},
                {"name": "Machine_Learning", "subtopics": ["supervised", "unsupervised", "reinforcement", "neural_networks", "deep_learning", "NLP", "computer_vision", "recommendation", "clustering", "overfitting"]},
                {"name": "Security", "subtopics": ["threats", "vulnerabilities", "OWASP", "encryption_security", "authentication", "authorization", "logging", "response", "recovery", "compliance"]},
                {"name": "DevOps", "subtopics": ["CI_CD", "containerisation", "orchestration", "monitoring", "infrastructure", "automation", "configuration", "deployment_strategies", "microservices", "serverless"]},
                {"name": "Database", "subtopics": [" normalisation", "indexing", "query_optimization", "transactions", "concurrency", "ACID_properties", "replication", "sharding", "partitioning", "data_warehousing"]},
                {"name": "Future", "subtopics": ["quantum_computing", "AI_alignment", "neuromorphic", "edge_computing", "UBIQUITOUS_computing", "ambient_intelligence", "brain_computer", "singularity", "technological_unemployment", "digital_immortality"]}
            ]
        }
    }
}

CURRICULUM = COMPREHENSIVE_CURRICULUM
DIFFICULTY_LEVELS = 10
DEFAULT_LESSON_DURATION_MINUTES = 80
DEFAULT_TOPICS_PER_LESSON = 1
SUBTOPICS_PER_TOPIC = 10
LEVEL_LESSONS = {
    "early": {"total_topics": 10, "total_subtopics": 30, "lesson_duration": 80},
    "primary": {"total_topics": 10, "total_subtopics": 30, "lesson_duration": 80},
    "lower_secondary": {"total_topics": 10, "total_subtopics": 30, "lesson_duration": 80},
    "upper_secondary": {"total_topics": 10, "total_subtopics": 30, "lesson_duration": 80},
}

DAILY_SCHEDULE = {
    "early": {
        "start_time": "08:00", "end_time": "10:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Numbers", "subtopic": "counting", "duration": 30},
            {"time": "08:35", "subject": "break", "duration": 5},
            {"time": "08:40", "subject": "english", "topic": "Phonics", "subtopic": "letter_sounds", "duration": 30},
            {"time": "09:15", "subject": "break", "duration": 10},
            {"time": "09:25", "subject": "science", "topic": "Our Bodies", "subtopic": "body_parts", "duration": 30},
        ],
    },
    "primary": {
        "start_time": "08:00", "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Number", "subtopic": "place_value", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "topic": "Reading", "subtopic": "comprehension", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "science", "topic": "Biology", "subtopic": "cells", "duration": 40},
            {"time": "10:30", "subject": "break", "duration": 5},
            {"time": "10:35", "subject": "computing", "topic": "Digital", "subtopic": "devices", "duration": 40},
        ],
    },
    "lower_secondary": {
        "start_time": "08:00", "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Number", "subtopic": "integers", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "topic": "Literature", "subtopic": "novels", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "science", "topic": "Biology", "subtopic": "cells", "duration": 40},
            {"time": "10:30", "subject": "break", "duration": 5},
            {"time": "10:35", "subject": "computing", "topic": "Systems", "subtopic": "hardware", "duration": 40},
        ],
    },
    "upper_secondary": {
        "start_time": "08:00", "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Pure", "subtopic": "algebra", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "topic": "Literature", "subtopic": "Shakespeare", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "science", "topic": "Physics", "subtopic": "mechanics", "duration": 40},
            {"time": "10:30", "subject": "break", "duration": 5},
            {"time": "10:35", "subject": "computing", "topic": "Systems", "subtopic": "architecture", "duration": 40},
        ],
    },
}

AGE_GROUP_KEYS = ["early", "primary", "lower_secondary", "upper_secondary"]
AGE_GROUP_DISPLAY = {
    "early": "Early Years (3-5)",
    "primary": "Primary (5-11)",
    "lower_secondary": "Lower Secondary (11-14)",
    "upper_secondary": "Upper Secondary (14-18)",
}

ROBOT_STATE = {
    "IDLE": "IDLE",
    "LISTENING": "LISTENING",
    "TEACHING": "TEACHING",
    "ENGAGED": "ENGAGED",
    "MOVING": "MOVING",
}

STUDENT_DB_PATH = DATA_DIR / "students.db"
SESSION_LOG_PATH = DATA_DIR / "sessions"
LOG_LEVEL = logging.INFO

DEFAULT_TTS_VOICE = {
    "en": "en-US", "zh": "zh-CN", "fr": "fr-FR", "de": "de-DE",
    "es": "es-ES", "it": "it-IT", "pt": "pt-BR", "ar": "ar-SA",
}

import logging