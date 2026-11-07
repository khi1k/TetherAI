# Object-Oriented Prototype for Tether AI Technologies

class Service:
    """Represents a service offered by the business."""

    def __init__(self, name: str, price: float):
        self._name = name
        self._price = price

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    def __repr__(self) -> str:
        return f"Service({self._name}, ${self._price:.2f})"


class Visit:
    """Represents a single customer visit containing one or more services."""

    def __init__(self, services: list[Service] | None = None):
        self._services = services if services is not None else []

    def add_service(self, service: Service) -> None:
        self._services.append(service)

    @property
    def services(self) -> list[Service]:
        return list(self._services)

    def calculate_subtotal(self) -> float:
        return sum(service.price for service in self._services)


class Customer:
    """Represents a small business customer with a record of visits."""

    def __init__(self, name: str):
        self._name = name
        self._visits: list[Visit] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def visits(self) -> list[Visit]:
        return list(self._visits)

    def add_visit(self, visit: Visit) -> None:
        self._visits.append(visit)

    def calculate_total_spent(self) -> float:
        return sum(visit.calculate_subtotal() for visit in self._visits)


class Barbershop:
    """Manages business customers, visits, and revenue calculations."""

    def __init__(self, name: str):
        self._name = name
        self._customers: list[Customer] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def customers(self) -> list[Customer]:
        return list(self._customers)

    def register_customer(self, customer: Customer) -> None:
        if customer not in self._customers:
            self._customers.append(customer)

    def record_visit(self, customer: Customer, visit: Visit) -> None:
        self.register_customer(customer)
        customer.add_visit(visit)

    def calculate_total_daily_revenue(self) -> float:
        return sum(customer.calculate_total_spent() for customer in self._customers)


# Sample Data and Calculations
if __name__ == "__main__":
    # Instantiate the Barbershop
    shop = Barbershop("Tether AI Grooming Lounge")

    # Define available services
    haircut = Service("Haircut", 30.00)
    beard_trim = Service("Beard Trim", 15.00)
    shave = Service("Hot Towel Shave", 25.00)
    shampoo = Service("Shampoo & Style", 10.00)

    # Create customers
    alex = Customer("Alex Mercer")
    brian = Customer("Brian Jones")
    carlos = Customer("Carlos Reed")

    # Record Customer Visits
    # Visit 1: Alex gets a haircut and shampoo
    v1 = Visit([haircut, shampoo])
    shop.record_visit(alex, v1)

    # Visit 2: Brian gets a haircut and beard trim
    v2 = Visit([haircut, beard_trim])
    shop.record_visit(brian, v2)

    # Visit 3: Carlos gets a hot towel shave
    v3 = Visit([shave])
    shop.record_visit(carlos, v3)

    # Visit 4: Alex returns for a hot towel shave
    v4 = Visit([shave])
    shop.record_visit(alex, v4)

    # Print Report & Breakdown
    print("==================================================")
    print(f"   {shop.name.upper()} - DAILY REPORT (OOP)   ")
    print("==================================================")

    for customer in shop.customers:
        print(f"\nCustomer: {customer.name}")
        print(f"  Total Visits Today: {len(customer.visits)}")
        for i, visit in enumerate(customer.visits, 1):
            service_names = ", ".join(s.name for s in visit.services)
            print(f"    Visit {i}: {service_names} (${visit.calculate_subtotal():.2f})")
        print(f"  Total Spent: ${customer.calculate_total_spent():.2f}")

    # Calculate Total Daily Revenue
    total_revenue = shop.calculate_total_daily_revenue()
    print("\n--------------------------------------------------")
    print(f"Total Daily Revenue: ${total_revenue:.2f}")
    print("==================================================")
