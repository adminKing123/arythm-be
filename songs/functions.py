def get_slides(request):
    slides = [
        {
            "id": 1,
            "title": "Record Label & Music streaming",
            "description": (
                "There are many variations of passages of Lorem Ipsum available, "
                "but the majority have suffered alteration in some form, by injected humour, "
                "or randomised words which don't look even slightly believable"
            ),
            "img": "https://volna.volkovdesign.com/img/home/slide1.jpg",
            "btns": ["BUY NOW", "LEARN MORE"],
        },
        {
            "id": 2,
            "title": "Metallica and Slipknot feature in trailer for ‘Long Live Rock’ documentary",
            "description": (
                "It also features Rage Against The Machine, Guns N' Roses and a number of others"
            ),
            "img": "https://volna.volkovdesign.com/img/home/slide2.jpg",
            "btns": ["LEARN MORE", "WATCH VIDEO"],
        },
        {
            "id": 3,
            "title": "New Artist of Our Label",
            "description": (
                "There are many variations of passages of Lorem Ipsum available, "
                "but the majority have suffered alteration in some form, by injected humour, "
                "or randomised words which don't look even slightly believable"
            ),
            "img": "https://volna.volkovdesign.com/img/home/slide3.jpg",
            "btns": [None, "LEARN MORE"],
        },
    ]
    return slides
