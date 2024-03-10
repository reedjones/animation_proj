import json

class Storyboard:
    def __init__(self, sequences=None):
        if sequences is None:
            sequences = []
        self.sequences = sequences

    def add_sequence(self, sequence):
        self.sequences.append(sequence)

    def remove_sequence(self, sequence_id):
        for sequence in self.sequences:
            if sequence['id'] == sequence_id:
                self.sequences.remove(sequence)
                break

    def update_sequence(self, sequence_id, new_sequence):
        for idx, sequence in enumerate(self.sequences):
            if sequence['id'] == sequence_id:
                self.sequences[idx] = new_sequence
                break

    def get_sequence(self, sequence_id):
        for sequence in self.sequences:
            if sequence['id'] == sequence_id:
                return sequence
        return None

    def save_to_disk(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.sequences, f, indent=2)

    @classmethod
    def load_from_disk(cls, filename):
        with open(filename, 'r') as f:
            sequences = json.load(f)
        return cls(sequences)

    def __str__(self):
        return json.dumps(self.sequences, indent=2)




def test():
    # Example usage:
    # Create a storyboard instance
    storyboard = Storyboard()

    # Add sequences
    sequence1 = {
        "name": "Sequence 1: Disheveled Apartment",
        "id": "Disheveled Apartment",
        "action": "Black teenager and flamboyant rapper-like man having a surreal conversation",
        "visuals": "Surreal atmosphere, morphing objects, fractal folding of space",
        "aesthetic": "Psychedelic, unsettling, mind-bending"
    }
    storyboard.add_sequence(sequence1)

    # Save to disk
    storyboard.save_to_disk("storyboard.json")

    # Load from disk
    loaded_storyboard = Storyboard.load_from_disk("storyboard.json")

    # Print loaded storyboard
    print(loaded_storyboard)

    # Update sequence
    sequence1_updated = {
        "name": "Sequence 1: Disheveled Apartment (Updated)",
        "id": "Disheveled Apartment",
        "action": "Updated action",
        "visuals": "Updated visuals",
        "aesthetic": "Updated aesthetic"
    }
    loaded_storyboard.update_sequence("Disheveled Apartment", sequence1_updated)

    # Print updated storyboard
    print(loaded_storyboard)

    # Remove sequence
    loaded_storyboard.remove_sequence("Disheveled Apartment")

    # Print storyboard after removal
    print(loaded_storyboard)


if __name__ == '__main__':
    test()