from num2words import num2words


class TimeService:
    def __init__(self):
        self.hours_dict = {
            1: "een", 2: "twee", 3: "drie", 4: "vier", 5: "vijf", 6: "zes",
            7: "zeven", 8: "acht", 9: "negen", 10: "tien", 11: "elf", 12: "twaalf"
        }

    def time_to_dutch(self, hour: int, minute: int) -> str:
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12

        next_hour = display_hour + 1 if display_hour < 12 else 1

        if minute == 0:
            return f"{self.hours_dict[display_hour]} uur"
        elif minute == 15:
            return f"kwart over {self.hours_dict[display_hour]}"
        elif minute == 30:
            return f"half {self.hours_dict[next_hour]}"
        elif minute == 45:
            return f"kwart voor {self.hours_dict[next_hour]}"
        elif minute == 5:
            return f"vijf over {self.hours_dict[display_hour]}"
        elif minute == 10:
            return f"tien over {self.hours_dict[display_hour]}"
        elif minute == 20:
            return f"tien voor half {self.hours_dict[next_hour]}"
        elif minute == 25:
            return f"vijf voor half {self.hours_dict[next_hour]}"
        elif minute == 35:
            return f"vijf over half {self.hours_dict[next_hour]}"
        elif minute == 40:
            return f"tien over half {self.hours_dict[next_hour]}"
        elif minute == 50:
            return f"tien voor {self.hours_dict[next_hour]}"
        elif minute == 55:
            return f"vijf voor {self.hours_dict[next_hour]}"
        else:
            if minute < 30:
                return f"{num2words(minute, lang='nl')} over {self.hours_dict[display_hour]}"
            else:
                minutes_before = 60 - minute
                return f"{num2words(minutes_before, lang='nl')} voor {self.hours_dict[next_hour]}"