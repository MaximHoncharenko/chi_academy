// 1. Enums і Union
var Days;
(function (Days) {
    Days["Monday"] = "\u041F\u043E\u043D\u0435\u0434\u0456\u043B\u043E\u043A";
    Days["Tuesday"] = "\u0412\u0456\u0432\u0442\u043E\u0440\u043E\u043A";
    Days["Wednesday"] = "\u0421\u0435\u0440\u0435\u0434\u0430";
    Days["Thursday"] = "\u0427\u0435\u0442\u0432\u0435\u0440";
    Days["Friday"] = "\u041F'\u044F\u0442\u043D\u0438\u0446\u044F";
    Days["Saturday"] = "\u0421\u0443\u0431\u043E\u0442\u0430";
    Days["Sunday"] = "\u041D\u0435\u0434\u0456\u043B\u044F";
})(Days || (Days = {}));
function getActivity(day) {
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
console.log("".concat(Days.Monday, ": ").concat(getActivity(Days.Monday)));
console.log("".concat(Days.Sunday, ": ").concat(getActivity(Days.Sunday)));


// 2. Дженерики (Generics)


var Queue = /** @class */ (function () {
    function Queue() {
        this.items = [];
    }
    Queue.prototype.enqueue = function (item) {
        this.items.push(item);
    };
    Queue.prototype.dequeue = function () {
        if (this.items.length === 0) {
            throw new Error("Черга порожня");
        }
        return this.items.shift();
    };
    Queue.prototype.peek = function () {
        return this.items[0];
    };
    Queue.prototype.size = function () {
        return this.items.length;
    };
    Queue.prototype.isEmpty = function () {
        return this.items.length === 0;
    };
    return Queue;
}());
// Приклад використання
console.log("\n=== Дженерики ===");
var stringQueue = new Queue();
stringQueue.enqueue("Перший");
stringQueue.enqueue("Другий");
stringQueue.enqueue("Третій");
console.log("Черга рядків:");
console.log("\u0412\u0438\u0434\u0430\u043B\u0435\u043D\u043E: ".concat(stringQueue.dequeue()));
console.log("\u0420\u043E\u0437\u043C\u0456\u0440 \u0447\u0435\u0440\u0433\u0438: ".concat(stringQueue.size()));
var numberQueue = new Queue();
numberQueue.enqueue(10);
numberQueue.enqueue(20);
numberQueue.enqueue(30);
console.log("\nЧерга чисел:");
console.log("\u0412\u0438\u0434\u0430\u043B\u0435\u043D\u043E: ".concat(numberQueue.dequeue()));
console.log("\u041D\u0430\u0441\u0442\u0443\u043F\u043D\u0438\u0439 \u0435\u043B\u0435\u043C\u0435\u043D\u0442: ".concat(numberQueue.peek()));
function combine(input1, input2) {
    if (typeof input1 === "string" && typeof input2 === "string") {
        return input1 + input2;
    }
    else if (typeof input1 === "number" && typeof input2 === "number") {
        return input1 + input2;
    }
    else {
        throw new Error("Обидва аргументи повинні бути одного типу (string або number)");
    }
}
// Приклад використання
console.log("\n=== Type Aliases ===");
console.log("\u0420\u044F\u0434\u043A\u0438: ".concat(combine("Привіт, ", "світ!")));
console.log("\u0427\u0438\u0441\u043B\u0430: ".concat(combine(5, 10)));
try {
    console.log(combine("текст", 123));
}
catch (error) {
    console.log("\u041F\u043E\u043C\u0438\u043B\u043A\u0430: ".concat(error.message));
}
var Employee = /** @class */ (function () {
    function Employee(name, age, position, salary) {
        this.name = name;
        this.age = age;
        this.position = position;
        this.salary = salary;
    }
    Employee.prototype.getSalary = function () {
        return this.salary;
    };
    Employee.prototype.setSalary = function (newSalary) {
        if (newSalary < 0) {
            throw new Error("Зарплата не може бути від'ємною");
        }
        this.salary = newSalary;
    };
    Employee.prototype.increaseSalary = function (percentage) {
        this.salary = this.salary * (1 + percentage / 100);
    };
    Employee.prototype.getInfo = function () {
        return "".concat(this.name, ", ").concat(this.age, " \u0440\u043E\u043A\u0456\u0432, ").concat(this.position, ", \u0437\u0430\u0440\u043F\u043B\u0430\u0442\u0430: ").concat(this.salary, " \u0433\u0440\u043D");
    };
    return Employee;
}());
// Приклад використання
console.log("\n=== Інтерфейси ===");
var worker1 = new Employee("Іван Петренко", 30, "Розробник", 50000);
console.log(worker1.getInfo());
worker1.setSalary(55000);
console.log("\u041D\u043E\u0432\u0430 \u0437\u0430\u0440\u043F\u043B\u0430\u0442\u0430: ".concat(worker1.getSalary(), " \u0433\u0440\u043D"));
worker1.increaseSalary(10);
console.log("\u041F\u0456\u0441\u043B\u044F \u043F\u0456\u0434\u0432\u0438\u0449\u0435\u043D\u043D\u044F \u043D\u0430 10%: ".concat(worker1.getSalary(), " \u0433\u0440\u043D"));
var worker2 = new Employee("Марія Коваленко", 28, "Дизайнер", 45000);
console.log(worker2.getInfo());
