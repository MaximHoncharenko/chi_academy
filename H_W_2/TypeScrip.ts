// 1. Enums і Union

enum Days {
  Monday = "Понеділок",
  Tuesday = "Вівторок",
  Wednesday = "Середа",
  Thursday = "Четвер",
  Friday = "П'ятниця",
  Saturday = "Субота",
  Sunday = "Неділя"
}

function getActivity(day: Days): string {
  switch (day) {
    case Days.Monday:
      return "Початок робочого тижня - плануйте завдання";
    case Days.Tuesday:
      return "Продуктивна робота над проектами";
    case Days.Wednesday:
      return "Середина тижня - час для зустрічей";
    case Days.Thursday:
      return "Завершення основних завдань";
    case Days.Friday:
      return "Підведення підсумків тижня";
    case Days.Saturday:
      return "Час для хобі та саморозвитку";
    case Days.Sunday:
      return "Відпочинок та підготовка до нового тижня";
    default:
      return "Невідомий день";
  }
}

// Приклад використання
console.log("=== Enums і Union ===");
console.log(`${Days.Monday}: ${getActivity(Days.Monday)}`);
console.log(`${Days.Sunday}: ${getActivity(Days.Sunday)}`);

// 2. Дженерики (Generics)


class Queue<T> {
  private items: T[] = [];

  enqueue(item: T): void {
    this.items.push(item);
  }

  dequeue(): T | undefined {
    if (this.items.length === 0) {
      throw new Error("Черга порожня");
    }
    return this.items.shift();
  }

  peek(): T | undefined {
    return this.items[0];
  }

  size(): number {
    return this.items.length;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }
}

// Приклад використання
console.log("\n=== Дженерики ===");

const stringQueue = new Queue<string>();
stringQueue.enqueue("Перший");
stringQueue.enqueue("Другий");
stringQueue.enqueue("Третій");
console.log("Черга рядків:");
console.log(`Видалено: ${stringQueue.dequeue()}`);
console.log(`Розмір черги: ${stringQueue.size()}`);

const numberQueue = new Queue<number>();
numberQueue.enqueue(10);
numberQueue.enqueue(20);
numberQueue.enqueue(30);
console.log("\nЧерга чисел:");
console.log(`Видалено: ${numberQueue.dequeue()}`);
console.log(`Наступний елемент: ${numberQueue.peek()}`);


// 3. Type Aliases та Literal Types

type StringOrNumber = string | number;

function combine(input1: StringOrNumber, input2: StringOrNumber): StringOrNumber {
  if (typeof input1 === "string" && typeof input2 === "string") {
    return input1 + input2;
  } else if (typeof input1 === "number" && typeof input2 === "number") {
    return input1 + input2;
  } else {
    throw new Error("Обидва аргументи повинні бути одного типу (string або number)");
  }
}

// Приклад використання
console.log("\n=== Type Aliases ===");
console.log(`Рядки: ${combine("Привіт, ", "світ!")}`);
console.log(`Числа: ${combine(5, 10)}`);

try {
  console.log(combine("текст", 123));
} catch (error) {
  console.log(`Помилка: ${(error as Error).message}`);
}

// 4. Розширені можливості інтерфейсів

interface IPerson {
  name: string;
  age: number;
}

interface IWorker extends IPerson {
  position: string;
  salary: number;
}

class Employee implements IWorker {
  name: string;
  age: number;
  position: string;
  salary: number;

  constructor(name: string, age: number, position: string, salary: number) {
    this.name = name;
    this.age = age;
    this.position = position;
    this.salary = salary;
  }

  getSalary(): number {
    return this.salary;
  }

  setSalary(newSalary: number): void {
    if (newSalary < 0) {
      throw new Error("Зарплата не може бути від'ємною");
    }
    this.salary = newSalary;
  }

  increaseSalary(percentage: number): void {
    this.salary = this.salary * (1 + percentage / 100);
  }

  getInfo(): string {
    return `${this.name}, ${this.age} років, ${this.position}, зарплата: ${this.salary} грн`;
  }
}

// Приклад використання
console.log("\n=== Інтерфейси ===");
const worker1 = new Employee("Іван Петренко", 30, "Розробник", 50000);
console.log(worker1.getInfo());

worker1.setSalary(55000);
console.log(`Нова зарплата: ${worker1.getSalary()} грн`);

worker1.increaseSalary(10);
console.log(`Після підвищення на 10%: ${worker1.getSalary()} грн`);

const worker2 = new Employee("Марія Коваленко", 28, "Дизайнер", 45000);
console.log(worker2.getInfo());