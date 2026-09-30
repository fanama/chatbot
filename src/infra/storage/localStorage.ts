export class LocalStorage<T> {
  key: string;
  values: T[];

  constructor(key: string, defaultValues: T[]) {
    this.key = key;

    const localString = localStorage.getItem(key) || "[]";

    let localValues: T[] = [];
    try {
      const parsed = JSON.parse(localString);
      if (Array.isArray(parsed)) {
        localValues = parsed;
      }
    } catch {
      // A corrupted entry used to throw during module evaluation, which broke
      // the whole page: fall back to the defaults instead.
      console.warn(`localStorage["${key}"] is not valid JSON, using defaults`);
    }

    if (localValues.length <= 0) {
      this.values = defaultValues;
      localStorage.setItem(this.key, JSON.stringify(this.values));
      return;
    }

    this.values = localValues;
  }

  save(values: T[]) {
    this.values = values;
    try {
      localStorage.setItem(this.key, JSON.stringify(values));
    } catch (error) {
      // Quota exceeded: losing persistence is better than breaking the chat.
      console.error(`Failed to persist "${this.key}"`, error);
    }
  }

  getAll(): T[] {
    return this.values;
  }

  add(value: T): T[] {
    const values = [...this.values, value];
    this.save(values);
    return values;
  }

  remove(value: T): T[] {
    const values = this.values.filter((v) => v != value);
    this.save(values);
    return values;
  }

  removeAll(): T[] {
    // Was `localStorage.clear()`: it wiped the history, the prompts and the user
    // session of every other key, not just this one.
    this.save([]);
    return this.values;
  }
}
