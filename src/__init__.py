def index_song(self, filepath, song_name=None):
    audio, sr = load_audio(filepath)
    fingerprints = fingerprint_audio(audio, sr)

    song_id = self._next_id
    self._next_id += 1

    if song_name is None:
        song_name = os.path.splitext(os.path.basename(filepath))[0]

    self.song_names[song_id] = song_name

    for hash_val, time_offset in fingerprints:
        self.table.insert(hash_val, (song_id, time_offset))

    print(f"Indexed: {song_name} ({len(fingerprints)} fingerprints)")

    return song_id


def index_directory(self, directory):
    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".wav")
    ]

    files.sort()

    for f in files:
        path = os.path.join(directory, f)
        self.index_song(path)

    print(f"\nIndexed {len(files)} song(s)")


def save(self, filepath):
    entries = []

    for bucket in self.table._buckets:
        for key, (song_id, time_offset) in bucket:
            entries.append([
                int(key),
                int(song_id),
                int(time_offset)
            ])

    data = {
        "song_names": {str(k): v for k, v in self.song_names.items()},
        "next_id": self._next_id,
        "capacity": self.table._capacity,
        "entries": entries
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(data, f)

    print(f"Database saved to {filepath}")


@classmethod
def load(cls, filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    db = cls()

    db.song_names = {int(k): v for k, v in data["song_names"].items()}
    db._next_id = data["next_id"]

    db.table = HashTable(capacity=data["capacity"])

    for key, song_id, time_offset in data["entries"]:
        db.table.insert(key, (song_id, time_offset))

    return db