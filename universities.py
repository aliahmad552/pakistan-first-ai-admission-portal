# university_data.py

def get_merit_chart_data(university):
    data = {
        "UET Lahore": {
            "labels": ["Engineering (All)", "Computer Science", "Electrical Engg", "Civil Engg", "Mechanical Engg"],
            "values": [85, 82, 80, 78, 79]
        },
        "NUST": {
            "labels": ["Engineering", "Computer Science", "Mechanical Engg", "Electrical Engg", "Software Engg"],
            "values": [88, 85, 82, 80, 83]
        },
        "FAST": {
            "labels": ["Computer Science", "Software Engineering", "Electrical Engg", "Bioinformatics"],
            "values": [90, 88, 85, 78]
        },
        "GCU Lahore": {
            "labels": ["Mathematics", "Physics", "Chemistry", "Biology"],
            "values": [75, 73, 70, 68]
        },
        "COMSATS": {
            "labels": ["Engineering", "Computer Science", "Business"],
            "values": [78, 75, 70]
        },
        "PU Lahore": {
            "labels": ["Science", "Arts", "Commerce"],
            "values": [70, 65, 60]
        },
        "GIKI": {
            "labels": ["Engineering", "Computer Science"],
            "values": [85, 83]
        },
        "LUMS": {
            "labels": ["Business", "Law", "Computer Science"],
            "values": [88, 85, 82]
        },
        "IBA Karachi": {
            "labels": ["Business", "Computer Science", "Economics"],
            "values": [82, 80, 75]
        },
        "NED University": {
            "labels": ["Engineering", "Computer Science"],
            "values": [75, 72]
        },
        "Bahria University": {
            "labels": ["Engineering", "Business", "Computer Science"],
            "values": [70, 68, 65]
        },
        "Air University": {
            "labels": ["Engineering", "Computer Science"],
            "values": [76, 72]
        },
        "QAU Islamabad": {
            "labels": ["Biological Sciences", "Chemistry", "Physics"],
            "values": [82, 78, 75]
        },
        "UMT Lahore": {
            "labels": ["Computer Science", "Business"],
            "values": [65, 60]
        },
        "UCP Lahore": {
            "labels": ["Computer Science", "Business"],
            "values": [68, 62]
        },
        "UET Taxila": {
            "labels": ["Engineering", "Computer Science"],
            "values": [80, 77]
        },
        "SZABIST": {
            "labels": ["Business", "Computer Science"],
            "values": [70, 68]
        },
        "IST": {
            "labels": ["Aerospace Engg", "Avionics Engg", "Computer Science"],
            "values": [84, 82, 80]
        },
        "Riphah International": {
            "labels": ["Engineering", "Medical", "Computer Science"],
            "values": [73, 78, 70]
        },
        "Superior University": {
            "labels": ["Business", "Computer Science"],
            "values": [60, 58]
        },
        "Dow University": {
            "labels": ["Medical", "Pharmacy"],
            "values": [87, 82]
        },
        "NUMS": {
            "labels": ["MBBS", "BDS", "Biological Sciences"],
            "values": [90, 88, 85]
        },
        "Arid Agriculture": {
            "labels": ["Agriculture", "CS", "Food Science"],
            "values": [70, 68, 65]
        },
        "KFUEIT": {
            "labels": ["Engineering", "Computer Science"],
            "values": [65, 60]
        },
        "Islamia University": {
            "labels": ["Business", "Computer Science"],
            "values": [62, 60]
        },
        "Abbottabad University": {
            "labels": ["Natural Sciences", "Computer Science"],
            "values": [68, 65]
        },
        "University of Peshawar": {
            "labels": ["Science", "Arts"],
            "values": [72, 68]
        },
        "Bahauddin Zakariya": {
            "labels": ["Engineering", "Business"],
            "values": [70, 67]
        },
        "University of Sargodha": {
            "labels": ["Science", "Education"],
            "values": [68, 65]
        },
        "Allama Iqbal Open University": {
            "labels": ["General Programs"],
            "values": [60]
        },
        "University of Karachi": {
            "labels": ["Science", "Commerce"],
            "values": [70, 68]
        },
        "University of Sindh": {
            "labels": ["Arts", "Social Sciences"],
            "values": [65, 62]
        },
        "GCUF": {
            "labels": ["Science", "Arts"],
            "values": [67, 64]
        },
        "Hazara University": {
            "labels": ["Science", "Computer Science"],
            "values": [66, 63]
        },
        "Ziauddin University": {
            "labels": ["Medical", "Pharmacy"],
            "values": [85, 80]
        },
        "HITEC University": {
            "labels": ["Engineering", "Computer Science"],
            "values": [78, 75]
        },
        "Iqra University": {
            "labels": ["Business", "Computer Science"],
            "values": [72, 70]
        },
        "UMT Sialkot": {
            "labels": ["Business", "Computer Science"],
            "values": [60, 58]
        },
        "University of Education": {
            "labels": ["Education", "Science"],
            "values": [65, 63]
        },
    }
    return data.get(university, {
        "labels": ["General Field 1", "General Field 2", "General Field 3"],
        "values": [70, 65, 60]
    })
