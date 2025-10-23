#!/usr/bin/env python3
"""
Backend Testing Suite for Espacios Con Piscina - Category System
Tests the new category functionality and role-based permissions
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://villa-expense-mgr.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.employee_token = None
        self.created_categories = []
        self.created_villas = []
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, token: str = None) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def test_health_check(self):
        """Test backend health"""
        result = self.make_request("GET", "/health")
        
        if result.get("success"):
            self.log_test("Health Check", True, "Backend is healthy")
        else:
            self.log_test("Health Check", False, "Backend health check failed", result)
    
    def test_register_admin(self):
        """Register admin user"""
        admin_data = {
            "username": "admin",
            "password": "admin123",
            "email": "admin@test.com",
            "full_name": "Admin User",
            "role": "admin"
        }
        
        result = self.make_request("POST", "/auth/register", admin_data)
        
        if result.get("success"):
            self.log_test("Register Admin", True, "Admin user registered successfully")
        elif result.get("status_code") == 400 and "already registered" in str(result.get("data", {})):
            self.log_test("Register Admin", True, "Admin user already exists")
        else:
            self.log_test("Register Admin", False, "Failed to register admin", result)
    
    def test_register_employee(self):
        """Register employee user"""
        employee_data = {
            "username": "emp1",
            "password": "emp123",
            "email": "emp@test.com",
            "full_name": "Empleado Test",
            "role": "employee"
        }
        
        result = self.make_request("POST", "/auth/register", employee_data)
        
        if result.get("success"):
            self.log_test("Register Employee", True, "Employee user registered successfully")
        elif result.get("status_code") == 400 and "already registered" in str(result.get("data", {})):
            self.log_test("Register Employee", True, "Employee user already exists")
        else:
            self.log_test("Register Employee", False, "Failed to register employee", result)
    
    def test_admin_login(self):
        """Login as admin"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        
        if result.get("success"):
            self.admin_token = result["data"]["access_token"]
            user_role = result["data"]["user"]["role"]
            if user_role == "admin":
                self.log_test("Admin Login", True, f"Admin logged in successfully, role: {user_role}")
            else:
                self.log_test("Admin Login", False, f"Wrong role returned: {user_role}")
        else:
            self.log_test("Admin Login", False, "Admin login failed", result)
    
    def test_employee_login(self):
        """Login as employee"""
        login_data = {
            "username": "emp1",
            "password": "emp123"
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        
        if result.get("success"):
            self.employee_token = result["data"]["access_token"]
            user_role = result["data"]["user"]["role"]
            if user_role == "employee":
                self.log_test("Employee Login", True, f"Employee logged in successfully, role: {user_role}")
            else:
                self.log_test("Employee Login", False, f"Wrong role returned: {user_role}")
        else:
            self.log_test("Employee Login", False, "Employee login failed", result)
    
    def test_create_categories_admin(self):
        """Create categories as admin"""
        categories = [
            {"name": "Premium", "description": "Villas premium de alta gama"},
            {"name": "Zona Norte", "description": "Villas ubicadas en zona norte"},
            {"name": "Económica", "description": "Villas económicas"}
        ]
        
        for cat_data in categories:
            result = self.make_request("POST", "/categories", cat_data, self.admin_token)
            
            if result.get("success"):
                category_id = result["data"]["id"]
                self.created_categories.append({"id": category_id, "name": cat_data["name"]})
                self.log_test(f"Create Category '{cat_data['name']}'", True, f"Category created with ID: {category_id}")
            else:
                self.log_test(f"Create Category '{cat_data['name']}'", False, "Failed to create category", result)
    
    def test_get_categories_admin(self):
        """Get categories as admin - verify alphabetical order"""
        result = self.make_request("GET", "/categories", token=self.admin_token)
        
        if result.get("success"):
            categories = result["data"]
            if len(categories) >= 3:
                # Check alphabetical order
                names = [cat["name"] for cat in categories]
                sorted_names = sorted(names, key=str.lower)
                
                if names == sorted_names:
                    self.log_test("Get Categories (Admin)", True, f"Categories retrieved in alphabetical order: {names}")
                else:
                    self.log_test("Get Categories (Admin)", False, f"Categories not in alphabetical order. Got: {names}, Expected: {sorted_names}")
            else:
                self.log_test("Get Categories (Admin)", False, f"Expected at least 3 categories, got {len(categories)}")
        else:
            self.log_test("Get Categories (Admin)", False, "Failed to get categories", result)
    
    def test_update_category_admin(self):
        """Update a category as admin"""
        if not self.created_categories:
            self.log_test("Update Category (Admin)", False, "No categories available to update")
            return
        
        category = self.created_categories[0]
        update_data = {
            "name": f"{category['name']} Updated",
            "description": "Updated description"
        }
        
        result = self.make_request("PUT", f"/categories/{category['id']}", update_data, self.admin_token)
        
        if result.get("success"):
            self.log_test("Update Category (Admin)", True, f"Category updated successfully")
        else:
            self.log_test("Update Category (Admin)", False, "Failed to update category", result)
    
    def test_get_single_category_admin(self):
        """Get single category by ID as admin"""
        if not self.created_categories:
            self.log_test("Get Single Category (Admin)", False, "No categories available to retrieve")
            return
        
        category = self.created_categories[0]
        result = self.make_request("GET", f"/categories/{category['id']}", token=self.admin_token)
        
        if result.get("success"):
            retrieved_cat = result["data"]
            if retrieved_cat["id"] == category["id"]:
                self.log_test("Get Single Category (Admin)", True, f"Category retrieved successfully: {retrieved_cat['name']}")
            else:
                self.log_test("Get Single Category (Admin)", False, "Retrieved category ID mismatch")
        else:
            self.log_test("Get Single Category (Admin)", False, "Failed to get single category", result)
    
    def test_create_villas_with_categories(self):
        """Create villas with and without categories"""
        if len(self.created_categories) < 2:
            self.log_test("Create Villas with Categories", False, "Need at least 2 categories for this test")
            return
        
        # Find Premium category
        premium_cat = next((cat for cat in self.created_categories if "Premium" in cat["name"]), None)
        if not premium_cat:
            self.log_test("Create Villas with Categories", False, "Premium category not found")
            return
        
        villas = [
            {
                "code": "PREM001",
                "name": "Villa Premium Deluxe",
                "description": "Villa premium con todas las comodidades",
                "location": "Zona Norte",
                "bedrooms": 4,
                "bathrooms": 3,
                "max_guests": 8,
                "price_per_night": 250.0,
                "currency": "USD",
                "category_id": premium_cat["id"]
            },
            {
                "code": "PREM002", 
                "name": "Villa Premium Ocean View",
                "description": "Villa premium con vista al mar",
                "location": "Costa Norte",
                "bedrooms": 3,
                "bathrooms": 2,
                "max_guests": 6,
                "price_per_night": 300.0,
                "currency": "USD",
                "category_id": premium_cat["id"]
            },
            {
                "code": "STD001",
                "name": "Villa Estándar",
                "description": "Villa sin categoría asignada",
                "location": "Centro",
                "bedrooms": 2,
                "bathrooms": 1,
                "max_guests": 4,
                "price_per_night": 100.0,
                "currency": "USD"
                # No category_id
            }
        ]
        
        for villa_data in villas:
            result = self.make_request("POST", "/villas", villa_data, self.admin_token)
            
            if result.get("success"):
                villa_id = result["data"]["id"]
                self.created_villas.append({"id": villa_id, "code": villa_data["code"], "category_id": villa_data.get("category_id")})
                category_info = f"with category {premium_cat['name']}" if villa_data.get("category_id") else "without category"
                self.log_test(f"Create Villa '{villa_data['code']}'", True, f"Villa created {category_info}")
            else:
                self.log_test(f"Create Villa '{villa_data['code']}'", False, "Failed to create villa", result)
    
    def test_get_all_villas(self):
        """Get all villas"""
        result = self.make_request("GET", "/villas", token=self.admin_token)
        
        if result.get("success"):
            villas = result["data"]
            villa_count = len(villas)
            self.log_test("Get All Villas", True, f"Retrieved {villa_count} villas")
        else:
            self.log_test("Get All Villas", False, "Failed to get villas", result)
    
    def test_search_villas(self):
        """Test villa search functionality"""
        if not self.created_villas:
            self.log_test("Search Villas", False, "No villas available for search test")
            return
        
        # Search by name
        search_term = "Premium"
        result = self.make_request("GET", "/villas", {"search": search_term}, self.admin_token)
        
        if result.get("success"):
            villas = result["data"]
            matching_villas = [v for v in villas if search_term.lower() in v.get("name", "").lower()]
            
            if len(matching_villas) > 0:
                self.log_test("Search Villas by Name", True, f"Found {len(matching_villas)} villas matching '{search_term}'")
            else:
                self.log_test("Search Villas by Name", False, f"No villas found matching '{search_term}'")
        else:
            self.log_test("Search Villas by Name", False, "Villa search failed", result)
    
    def test_filter_villas_by_category(self):
        """Test villa filtering by category"""
        if not self.created_categories:
            self.log_test("Filter Villas by Category", False, "No categories available for filter test")
            return
        
        premium_cat = next((cat for cat in self.created_categories if "Premium" in cat["name"]), None)
        if not premium_cat:
            self.log_test("Filter Villas by Category", False, "Premium category not found")
            return
        
        result = self.make_request("GET", "/villas", {"category_id": premium_cat["id"]}, self.admin_token)
        
        if result.get("success"):
            villas = result["data"]
            premium_villas = [v for v in villas if v.get("category_id") == premium_cat["id"]]
            
            if len(premium_villas) >= 2:
                self.log_test("Filter Villas by Category", True, f"Found {len(premium_villas)} villas in Premium category")
            else:
                self.log_test("Filter Villas by Category", False, f"Expected at least 2 Premium villas, found {len(premium_villas)}")
        else:
            self.log_test("Filter Villas by Category", False, "Villa category filter failed", result)
    
    def test_delete_category_and_unassign_villas(self):
        """Delete category and verify villas are unassigned"""
        # Find Económica category
        economica_cat = next((cat for cat in self.created_categories if "Económica" in cat["name"]), None)
        if not economica_cat:
            self.log_test("Delete Category", False, "Económica category not found")
            return
        
        # Delete the category
        result = self.make_request("DELETE", f"/categories/{economica_cat['id']}", token=self.admin_token)
        
        if result.get("success"):
            self.log_test("Delete Category", True, "Económica category deleted successfully")
            
            # Verify villas are unassigned
            villas_result = self.make_request("GET", "/villas", token=self.admin_token)
            if villas_result.get("success"):
                villas = villas_result["data"]
                unassigned_villas = [v for v in villas if v.get("category_id") is None]
                self.log_test("Verify Villa Unassignment", True, f"Found {len(unassigned_villas)} villas without category after deletion")
            else:
                self.log_test("Verify Villa Unassignment", False, "Failed to verify villa unassignment")
        else:
            self.log_test("Delete Category", False, "Failed to delete category", result)
    
    def test_employee_permissions(self):
        """Test employee permissions"""
        if not self.employee_token:
            self.log_test("Employee Permissions", False, "Employee token not available")
            return
        
        # Employee CAN view categories (for selection)
        result = self.make_request("GET", "/categories", token=self.employee_token)
        if result.get("success"):
            self.log_test("Employee View Categories", True, "Employee can view categories")
        else:
            self.log_test("Employee View Categories", False, "Employee cannot view categories", result)
        
        # Employee CANNOT create categories (should get 403)
        category_data = {"name": "Test Category", "description": "Should fail"}
        result = self.make_request("POST", "/categories", category_data, self.employee_token)
        
        if result.get("status_code") == 403:
            self.log_test("Employee Create Category (Forbidden)", True, "Employee correctly forbidden from creating categories")
        elif result.get("status_code") == 401:
            self.log_test("Employee Create Category (Forbidden)", True, "Employee correctly unauthorized to create categories")
        else:
            self.log_test("Employee Create Category (Forbidden)", False, f"Expected 403/401, got {result.get('status_code')}", result)
        
        # Employee CAN view villas
        result = self.make_request("GET", "/villas", token=self.employee_token)
        if result.get("success"):
            villas = result["data"]
            self.log_test("Employee View Villas", True, f"Employee can view {len(villas)} villas")
        else:
            self.log_test("Employee View Villas", False, "Employee cannot view villas", result)

    def test_auto_expense_creation_flow(self):
        """Test auto-creation of expenses when reservation has owner_price > 0"""
        print("\n💰 Testing Auto-Expense Creation Flow")
        
        # Step 1: Get villas with owner_price configured
        villas_result = self.make_request("GET", "/villas", token=self.admin_token)
        if not villas_result.get("success"):
            self.log_test("Get Villas for Expense Test", False, "Failed to get villas", villas_result)
            return
        
        villas = villas_result["data"]
        if not villas:
            self.log_test("Get Villas for Expense Test", False, "No villas available for testing")
            return
        
        # Use the first villa
        test_villa = villas[0]
        self.log_test("Get Villas for Expense Test", True, f"Using villa: {test_villa['code']}")
        
        # Step 2: Get customers
        customers_result = self.make_request("GET", "/customers", token=self.admin_token)
        if not customers_result.get("success"):
            # Create a test customer if none exist
            customer_data = {
                "name": "María González",
                "phone": "809-555-1234",
                "email": "maria.gonzalez@email.com",
                "address": "Santo Domingo, República Dominicana"
            }
            create_result = self.make_request("POST", "/customers", customer_data, self.admin_token)
            if create_result.get("success"):
                test_customer = create_result["data"]
                self.log_test("Create Test Customer", True, f"Created customer: {test_customer['name']}")
            else:
                self.log_test("Create Test Customer", False, "Failed to create test customer", create_result)
                return
        else:
            customers = customers_result["data"]
            if customers:
                test_customer = customers[0]
                self.log_test("Get Customers for Expense Test", True, f"Using customer: {test_customer['name']}")
            else:
                # Create a test customer
                customer_data = {
                    "name": "María González",
                    "phone": "809-555-1234", 
                    "email": "maria.gonzalez@email.com",
                    "address": "Santo Domingo, República Dominicana"
                }
                create_result = self.make_request("POST", "/customers", customer_data, self.admin_token)
                if create_result.get("success"):
                    test_customer = create_result["data"]
                    self.log_test("Create Test Customer", True, f"Created customer: {test_customer['name']}")
                else:
                    self.log_test("Create Test Customer", False, "Failed to create test customer", create_result)
                    return
        
        # Step 3: Create reservation with owner_price > 0
        reservation_data = {
            "customer_id": test_customer["id"],
            "customer_name": test_customer["name"],
            "villa_id": test_villa["id"],
            "villa_code": test_villa["code"],
            "rental_type": "pasadia",
            "reservation_date": "2024-01-15T00:00:00Z",
            "check_in_time": "9:00 AM",
            "check_out_time": "8:00 PM",
            "guests": 6,
            "base_price": 15000.0,
            "owner_price": 8000.0,  # IMPORTANT: > 0 to trigger auto-expense
            "subtotal": 15000.0,
            "total_amount": 15000.0,
            "amount_paid": 7500.0,
            "currency": "DOP",
            "status": "confirmed",
            "notes": "Test reservation for auto-expense creation"
        }
        
        # Get expenses count before creating reservation
        expenses_before_result = self.make_request("GET", "/expenses", token=self.admin_token)
        expenses_before_count = len(expenses_before_result["data"]) if expenses_before_result.get("success") else 0
        
        reservation_result = self.make_request("POST", "/reservations", reservation_data, self.admin_token)
        
        if not reservation_result.get("success"):
            self.log_test("Create Reservation with Owner Price", False, "Failed to create reservation", reservation_result)
            return
        
        created_reservation = reservation_result["data"]
        self.log_test("Create Reservation with Owner Price", True, f"Created reservation #{created_reservation['invoice_number']} with owner_price: {reservation_data['owner_price']}")
        
        # Step 4: Verify auto-created expense
        expenses_after_result = self.make_request("GET", "/expenses", token=self.admin_token)
        
        if not expenses_after_result.get("success"):
            self.log_test("Get Expenses After Reservation", False, "Failed to get expenses", expenses_after_result)
            return
        
        expenses_after = expenses_after_result["data"]
        expenses_after_count = len(expenses_after)
        
        # Check if a new expense was created
        if expenses_after_count > expenses_before_count:
            self.log_test("Expense Count Increased", True, f"Expenses increased from {expenses_before_count} to {expenses_after_count}")
            
            # Find the auto-created expense
            auto_expense = None
            for expense in expenses_after:
                if (expense.get("category") == "pago_propietario" and 
                    expense.get("related_reservation_id") == created_reservation["id"]):
                    auto_expense = expense
                    break
            
            if auto_expense:
                # Verify expense details
                checks = []
                
                # Check category
                if auto_expense.get("category") == "pago_propietario":
                    checks.append("✓ Category: pago_propietario")
                else:
                    checks.append(f"✗ Category: {auto_expense.get('category')} (expected: pago_propietario)")
                
                # Check amount
                if auto_expense.get("amount") == 8000.0:
                    checks.append("✓ Amount: 8000.0")
                else:
                    checks.append(f"✗ Amount: {auto_expense.get('amount')} (expected: 8000.0)")
                
                # Check description contains villa code
                description = auto_expense.get("description", "")
                if test_villa["code"] in description:
                    checks.append(f"✓ Description contains villa code: {test_villa['code']}")
                else:
                    checks.append(f"✗ Description missing villa code: {description}")
                
                # Check related_reservation_id
                if auto_expense.get("related_reservation_id") == created_reservation["id"]:
                    checks.append("✓ Related reservation ID matches")
                else:
                    checks.append(f"✗ Related reservation ID: {auto_expense.get('related_reservation_id')}")
                
                # Check payment_status
                if auto_expense.get("payment_status") == "pending":
                    checks.append("✓ Payment status: pending")
                else:
                    checks.append(f"✗ Payment status: {auto_expense.get('payment_status')} (expected: pending)")
                
                # Check currency
                if auto_expense.get("currency") == "DOP":
                    checks.append("✓ Currency: DOP")
                else:
                    checks.append(f"✗ Currency: {auto_expense.get('currency')} (expected: DOP)")
                
                all_checks_passed = all("✓" in check for check in checks)
                
                if all_checks_passed:
                    self.log_test("Auto-Created Expense Verification", True, f"All expense fields correct:\n   " + "\n   ".join(checks))
                else:
                    self.log_test("Auto-Created Expense Verification", False, f"Some expense fields incorrect:\n   " + "\n   ".join(checks))
                
                # Log the full expense for debugging
                print(f"   📋 Auto-created expense details:")
                print(f"      ID: {auto_expense.get('id')}")
                print(f"      Category: {auto_expense.get('category')}")
                print(f"      Amount: {auto_expense.get('amount')} {auto_expense.get('currency')}")
                print(f"      Description: {auto_expense.get('description')}")
                print(f"      Payment Status: {auto_expense.get('payment_status')}")
                print(f"      Related Reservation: {auto_expense.get('related_reservation_id')}")
                
            else:
                self.log_test("Find Auto-Created Expense", False, "No expense found with category 'pago_propietario' and matching reservation ID")
                
                # Debug: show all expenses
                print("   🔍 All expenses found:")
                for i, expense in enumerate(expenses_after):
                    print(f"      {i+1}. Category: {expense.get('category')}, Amount: {expense.get('amount')}, Related: {expense.get('related_reservation_id')}")
        else:
            self.log_test("Expense Count Increased", False, f"No new expenses created. Count remained at {expenses_before_count}")
        
        # Step 5: Verify expense structure and auto-generated flag
        if 'auto_expense' in locals() and auto_expense:
            # Check if expense has proper structure
            required_fields = ["id", "category", "description", "amount", "currency", "expense_date", "payment_status", "related_reservation_id", "created_at", "created_by"]
            missing_fields = [field for field in required_fields if field not in auto_expense]
            
            if not missing_fields:
                self.log_test("Expense Structure Complete", True, "All required fields present in auto-created expense")
            else:
                self.log_test("Expense Structure Complete", False, f"Missing fields: {missing_fields}")
        
        print(f"   🎯 TEST SUMMARY: Auto-expense creation flow {'✅ PASSED' if all_checks_passed else '❌ FAILED'}")
        return auto_expense if 'auto_expense' in locals() else None

    def test_customer_dni_field(self):
        """Test DNI field functionality in Customer model"""
        print("\n📋 Testing Customer DNI Field")
        
        # Test 1: Create customer WITH DNI
        customer_with_dni = {
            "name": "Juan Pérez",
            "phone": "809-555-1234",
            "dni": "001-1234567-8",
            "email": "juan@test.com"
        }
        
        result = self.make_request("POST", "/customers", customer_with_dni, self.admin_token)
        
        if result.get("success"):
            created_customer = result["data"]
            if created_customer.get("dni") == "001-1234567-8":
                self.log_test("Create Customer WITH DNI", True, f"Customer created with DNI: {created_customer['dni']}")
                customer_with_dni_id = created_customer["id"]
            else:
                self.log_test("Create Customer WITH DNI", False, f"DNI field missing or incorrect: {created_customer.get('dni')}")
                return
        else:
            self.log_test("Create Customer WITH DNI", False, "Failed to create customer with DNI", result)
            return
        
        # Test 2: Create customer WITHOUT DNI (optional field)
        customer_without_dni = {
            "name": "María González",
            "phone": "809-555-5678",
            "email": "maria@test.com"
        }
        
        result = self.make_request("POST", "/customers", customer_without_dni, self.admin_token)
        
        if result.get("success"):
            created_customer = result["data"]
            # DNI should be None or not present
            dni_value = created_customer.get("dni")
            if dni_value is None or dni_value == "":
                self.log_test("Create Customer WITHOUT DNI", True, "Customer created successfully without DNI field")
                customer_without_dni_id = created_customer["id"]
            else:
                self.log_test("Create Customer WITHOUT DNI", False, f"Unexpected DNI value: {dni_value}")
                return
        else:
            self.log_test("Create Customer WITHOUT DNI", False, "Failed to create customer without DNI", result)
            return
        
        # Test 3: Get customers list and verify DNI field is present
        result = self.make_request("GET", "/customers", token=self.admin_token)
        
        if result.get("success"):
            customers = result["data"]
            
            # Find our test customers
            customer_with_dni_found = None
            customer_without_dni_found = None
            
            for customer in customers:
                if customer.get("id") == customer_with_dni_id:
                    customer_with_dni_found = customer
                elif customer.get("id") == customer_without_dni_id:
                    customer_without_dni_found = customer
            
            # Verify customer with DNI
            if customer_with_dni_found:
                if customer_with_dni_found.get("dni") == "001-1234567-8":
                    self.log_test("Verify Customer WITH DNI in List", True, f"DNI field present and correct: {customer_with_dni_found['dni']}")
                else:
                    self.log_test("Verify Customer WITH DNI in List", False, f"DNI field incorrect: {customer_with_dni_found.get('dni')}")
            else:
                self.log_test("Verify Customer WITH DNI in List", False, "Customer with DNI not found in list")
            
            # Verify customer without DNI
            if customer_without_dni_found:
                dni_value = customer_without_dni_found.get("dni")
                if dni_value is None or dni_value == "":
                    self.log_test("Verify Customer WITHOUT DNI in List", True, "Customer without DNI correctly shows no DNI value")
                else:
                    self.log_test("Verify Customer WITHOUT DNI in List", False, f"Unexpected DNI value: {dni_value}")
            else:
                self.log_test("Verify Customer WITHOUT DNI in List", False, "Customer without DNI not found in list")
            
            # Test 4: Verify DNI field structure in API response
            dni_field_present = any("dni" in customer for customer in customers)
            if dni_field_present:
                self.log_test("DNI Field Structure", True, "DNI field is present in customer API responses")
            else:
                self.log_test("DNI Field Structure", False, "DNI field missing from customer API responses")
                
        else:
            self.log_test("Get Customers List", False, "Failed to get customers list", result)

    def test_auto_generated_expense_deletion(self):
        """Test deletion of auto-generated expenses"""
        print("\n🗑️ Testing Auto-Generated Expense Deletion")
        
        # Step 1: Create a reservation with owner_price > 0 to generate an auto-expense
        # Get a villa first
        villas_result = self.make_request("GET", "/villas", token=self.admin_token)
        if not villas_result.get("success") or not villas_result["data"]:
            self.log_test("Get Villa for Expense Deletion Test", False, "No villas available")
            return
        
        test_villa = villas_result["data"][0]
        
        # Get a customer
        customers_result = self.make_request("GET", "/customers", token=self.admin_token)
        if not customers_result.get("success") or not customers_result["data"]:
            self.log_test("Get Customer for Expense Deletion Test", False, "No customers available")
            return
        
        test_customer = customers_result["data"][0]
        
        # Create reservation with owner_price > 0
        reservation_data = {
            "customer_id": test_customer["id"],
            "customer_name": test_customer["name"],
            "villa_id": test_villa["id"],
            "villa_code": test_villa["code"],
            "rental_type": "pasadia",
            "reservation_date": "2024-01-16T00:00:00Z",
            "check_in_time": "10:00 AM",
            "check_out_time": "6:00 PM",
            "guests": 4,
            "base_price": 12000.0,
            "owner_price": 5000.0,  # This will trigger auto-expense creation
            "subtotal": 12000.0,
            "total_amount": 12000.0,
            "amount_paid": 6000.0,
            "currency": "DOP",
            "status": "confirmed",
            "notes": "Test reservation for expense deletion"
        }
        
        reservation_result = self.make_request("POST", "/reservations", reservation_data, self.admin_token)
        
        if not reservation_result.get("success"):
            self.log_test("Create Reservation for Expense Deletion", False, "Failed to create reservation", reservation_result)
            return
        
        created_reservation = reservation_result["data"]
        self.log_test("Create Reservation for Expense Deletion", True, f"Created reservation #{created_reservation['invoice_number']}")
        
        # Step 2: Get expenses and find the auto-generated one
        expenses_result = self.make_request("GET", "/expenses", token=self.admin_token)
        
        if not expenses_result.get("success"):
            self.log_test("Get Expenses for Deletion Test", False, "Failed to get expenses", expenses_result)
            return
        
        expenses = expenses_result["data"]
        
        # Find the auto-generated expense
        auto_expense = None
        for expense in expenses:
            if (expense.get("category") == "pago_propietario" and 
                expense.get("related_reservation_id") == created_reservation["id"]):
                auto_expense = expense
                break
        
        if not auto_expense:
            self.log_test("Find Auto-Generated Expense", False, "Auto-generated expense not found")
            return
        
        self.log_test("Find Auto-Generated Expense", True, f"Found auto-generated expense with ID: {auto_expense['id']}")
        
        # Step 3: Verify the expense has related_reservation_id (marking it as auto-generated)
        if auto_expense.get("related_reservation_id"):
            self.log_test("Verify Auto-Generated Expense Marker", True, f"Expense has related_reservation_id: {auto_expense['related_reservation_id']}")
        else:
            self.log_test("Verify Auto-Generated Expense Marker", False, "Expense missing related_reservation_id")
        
        # Step 4: Attempt to delete the auto-generated expense (this MUST work now)
        delete_result = self.make_request("DELETE", f"/expenses/{auto_expense['id']}", token=self.admin_token)
        
        if delete_result.get("success"):
            self.log_test("Delete Auto-Generated Expense", True, "Auto-generated expense deleted successfully")
        else:
            self.log_test("Delete Auto-Generated Expense", False, f"Failed to delete auto-generated expense. Status: {delete_result.get('status_code')}", delete_result)
            return
        
        # Step 5: Verify the expense was actually deleted
        verify_result = self.make_request("GET", "/expenses", token=self.admin_token)
        
        if verify_result.get("success"):
            remaining_expenses = verify_result["data"]
            
            # Check if the deleted expense is still in the list
            deleted_expense_found = any(exp.get("id") == auto_expense["id"] for exp in remaining_expenses)
            
            if not deleted_expense_found:
                self.log_test("Verify Expense Deletion", True, "Auto-generated expense successfully removed from expenses list")
            else:
                self.log_test("Verify Expense Deletion", False, "Auto-generated expense still appears in expenses list")
        else:
            self.log_test("Verify Expense Deletion", False, "Failed to verify expense deletion", verify_result)
        
        # Step 6: Test deletion of a regular (non-auto-generated) expense for comparison
        # Create a manual expense
        manual_expense_data = {
            "category": "otros",  # Use valid category
            "description": "Test manual expense for deletion",
            "amount": 2500.0,
            "currency": "DOP",
            "expense_date": "2024-01-16T00:00:00Z",
            "payment_status": "pending",
            "notes": "Manual expense for testing deletion"
        }
        
        manual_expense_result = self.make_request("POST", "/expenses", manual_expense_data, self.admin_token)
        
        if manual_expense_result.get("success"):
            manual_expense = manual_expense_result["data"]
            self.log_test("Create Manual Expense", True, f"Created manual expense with ID: {manual_expense['id']}")
            
            # Try to delete the manual expense
            delete_manual_result = self.make_request("DELETE", f"/expenses/{manual_expense['id']}", token=self.admin_token)
            
            if delete_manual_result.get("success"):
                self.log_test("Delete Manual Expense", True, "Manual expense deleted successfully")
            else:
                self.log_test("Delete Manual Expense", False, "Failed to delete manual expense", delete_manual_result)
        else:
            self.log_test("Create Manual Expense", False, "Failed to create manual expense for comparison", manual_expense_result)
    
    def test_existing_expenses_with_types(self):
        """Test verification of existing expenses with expense_type field"""
        print("\n📋 Testing Existing Expenses with Types")
        
        # Get all expenses
        result = self.make_request("GET", "/expenses", token=self.admin_token)
        
        if not result.get("success"):
            self.log_test("Get All Expenses", False, "Failed to get expenses", result)
            return
        
        expenses = result["data"]
        self.log_test("Get All Expenses", True, f"Retrieved {len(expenses)} expenses")
        
        # Verify expense_type field presence and values
        expenses_with_type = []
        valid_types = ['variable', 'fijo', 'unico']
        
        for expense in expenses:
            expense_type = expense.get("expense_type")
            if expense_type:
                if expense_type in valid_types:
                    expenses_with_type.append({
                        "id": expense.get("id"),
                        "description": expense.get("description"),
                        "type": expense_type,
                        "amount": expense.get("amount")
                    })
                else:
                    self.log_test("Invalid Expense Type", False, f"Invalid expense_type '{expense_type}' found in expense: {expense.get('description')}")
        
        if expenses_with_type:
            # Count by type
            variable_count = len([e for e in expenses_with_type if e["type"] == "variable"])
            fijo_count = len([e for e in expenses_with_type if e["type"] == "fijo"])
            unico_count = len([e for e in expenses_with_type if e["type"] == "unico"])
            
            self.log_test("Existing Expenses by Type", True, 
                         f"Found expenses: {variable_count} variable, {fijo_count} fijo, {unico_count} unico")
            
            # Log details of existing expenses
            print("   📊 Existing expenses breakdown:")
            for expense in expenses_with_type:
                print(f"      - {expense['type'].upper()}: {expense['description']} (${expense['amount']})")
        else:
            self.log_test("Existing Expenses by Type", True, "No expenses with expense_type found (expected for new system)")
    
    def test_create_variable_expense(self):
        """Test creation of variable expense with specific fields"""
        print("\n🔄 Testing Variable Expense Creation")
        
        variable_expense_data = {
            "category": "otros",
            "description": "Compra de materiales de construcción",
            "amount": 5000.0,
            "currency": "DOP",
            "expense_date": "2025-01-25T00:00:00Z",
            "payment_status": "pending",
            "expense_type": "variable",
            "reservation_check_in": "2025-01-25T00:00:00Z",
            "notes": "Gasto variable para mejoras de villa"
        }
        
        result = self.make_request("POST", "/expenses", variable_expense_data, self.admin_token)
        
        if result.get("success"):
            created_expense = result["data"]
            
            # Verify all fields
            checks = []
            
            if created_expense.get("expense_type") == "variable":
                checks.append("✓ expense_type: variable")
            else:
                checks.append(f"✗ expense_type: {created_expense.get('expense_type')} (expected: variable)")
            
            if created_expense.get("amount") == 5000.0:
                checks.append("✓ amount: 5000.0")
            else:
                checks.append(f"✗ amount: {created_expense.get('amount')} (expected: 5000.0)")
            
            if created_expense.get("currency") == "DOP":
                checks.append("✓ currency: DOP")
            else:
                checks.append(f"✗ currency: {created_expense.get('currency')} (expected: DOP)")
            
            if created_expense.get("payment_status") == "pending":
                checks.append("✓ payment_status: pending")
            else:
                checks.append(f"✗ payment_status: {created_expense.get('payment_status')} (expected: pending)")
            
            # Check if reservation_check_in is present (variable-specific field)
            if "reservation_check_in" in created_expense:
                checks.append("✓ reservation_check_in: present")
            else:
                checks.append("✗ reservation_check_in: missing")
            
            all_checks_passed = all("✓" in check for check in checks)
            
            if all_checks_passed:
                self.log_test("Create Variable Expense", True, f"Variable expense created successfully:\n   " + "\n   ".join(checks))
                return created_expense
            else:
                self.log_test("Create Variable Expense", False, f"Variable expense creation issues:\n   " + "\n   ".join(checks))
        else:
            self.log_test("Create Variable Expense", False, "Failed to create variable expense", result)
        
        return None
    
    def test_create_fijo_expense(self):
        """Test creation of fijo (fixed) expense with recurring fields"""
        print("\n🔁 Testing Fijo Expense Creation")
        
        fijo_expense_data = {
            "category": "otros",
            "description": "Servicio de agua mensual",
            "amount": 800.0,
            "currency": "DOP",
            "expense_date": "2025-01-21T00:00:00Z",
            "payment_status": "pending",
            "expense_type": "fijo",
            "has_payment_reminder": True,
            "payment_reminder_day": 5,
            "is_recurring": True,
            "notes": "Gasto fijo mensual de agua"
        }
        
        result = self.make_request("POST", "/expenses", fijo_expense_data, self.admin_token)
        
        if result.get("success"):
            created_expense = result["data"]
            
            # Verify all fields
            checks = []
            
            if created_expense.get("expense_type") == "fijo":
                checks.append("✓ expense_type: fijo")
            else:
                checks.append(f"✗ expense_type: {created_expense.get('expense_type')} (expected: fijo)")
            
            if created_expense.get("amount") == 800.0:
                checks.append("✓ amount: 800.0")
            else:
                checks.append(f"✗ amount: {created_expense.get('amount')} (expected: 800.0)")
            
            if created_expense.get("has_payment_reminder") is True:
                checks.append("✓ has_payment_reminder: true")
            else:
                checks.append(f"✗ has_payment_reminder: {created_expense.get('has_payment_reminder')} (expected: true)")
            
            if created_expense.get("payment_reminder_day") == 5:
                checks.append("✓ payment_reminder_day: 5")
            else:
                checks.append(f"✗ payment_reminder_day: {created_expense.get('payment_reminder_day')} (expected: 5)")
            
            if created_expense.get("is_recurring") is True:
                checks.append("✓ is_recurring: true")
            else:
                checks.append(f"✗ is_recurring: {created_expense.get('is_recurring')} (expected: true)")
            
            all_checks_passed = all("✓" in check for check in checks)
            
            if all_checks_passed:
                self.log_test("Create Fijo Expense", True, f"Fijo expense created successfully:\n   " + "\n   ".join(checks))
                return created_expense
            else:
                self.log_test("Create Fijo Expense", False, f"Fijo expense creation issues:\n   " + "\n   ".join(checks))
        else:
            self.log_test("Create Fijo Expense", False, "Failed to create fijo expense", result)
        
        return None
    
    def test_create_unico_expense(self):
        """Test creation of unico (one-time) expense with paid status"""
        print("\n💰 Testing Unico Expense Creation")
        
        unico_expense_data = {
            "category": "otros",
            "description": "Compra de escritorio para oficina",
            "amount": 15000.0,
            "currency": "DOP",
            "expense_date": "2025-01-20T00:00:00Z",
            "payment_status": "paid",
            "expense_type": "unico",
            "notes": "Gasto único ya pagado"
        }
        
        result = self.make_request("POST", "/expenses", unico_expense_data, self.admin_token)
        
        if result.get("success"):
            created_expense = result["data"]
            
            # Verify all fields
            checks = []
            
            if created_expense.get("expense_type") == "unico":
                checks.append("✓ expense_type: unico")
            else:
                checks.append(f"✗ expense_type: {created_expense.get('expense_type')} (expected: unico)")
            
            if created_expense.get("amount") == 15000.0:
                checks.append("✓ amount: 15000.0")
            else:
                checks.append(f"✗ amount: {created_expense.get('amount')} (expected: 15000.0)")
            
            if created_expense.get("payment_status") == "paid":
                checks.append("✓ payment_status: paid")
            else:
                checks.append(f"✗ payment_status: {created_expense.get('payment_status')} (expected: paid)")
            
            if created_expense.get("currency") == "DOP":
                checks.append("✓ currency: DOP")
            else:
                checks.append(f"✗ currency: {created_expense.get('currency')} (expected: DOP)")
            
            all_checks_passed = all("✓" in check for check in checks)
            
            if all_checks_passed:
                self.log_test("Create Unico Expense", True, f"Unico expense created successfully:\n   " + "\n   ".join(checks))
                return created_expense
            else:
                self.log_test("Create Unico Expense", False, f"Unico expense creation issues:\n   " + "\n   ".join(checks))
        else:
            self.log_test("Create Unico Expense", False, "Failed to create unico expense", result)
        
        return None
    
    def test_update_expense_type(self):
        """Test updating expense type"""
        print("\n🔄 Testing Expense Type Update")
        
        # First create a test expense
        test_expense_data = {
            "category": "otros",
            "description": "Test expense for type update",
            "amount": 1000.0,
            "currency": "DOP",
            "expense_date": "2025-01-22T00:00:00Z",
            "payment_status": "pending",
            "expense_type": "variable"
        }
        
        create_result = self.make_request("POST", "/expenses", test_expense_data, self.admin_token)
        
        if not create_result.get("success"):
            self.log_test("Create Test Expense for Update", False, "Failed to create test expense", create_result)
            return
        
        created_expense = create_result["data"]
        expense_id = created_expense["id"]
        
        self.log_test("Create Test Expense for Update", True, f"Created test expense with ID: {expense_id}")
        
        # Update the expense type from 'variable' to 'fijo'
        update_data = {
            "expense_type": "fijo",
            "has_payment_reminder": True,
            "payment_reminder_day": 10,
            "is_recurring": True
        }
        
        update_result = self.make_request("PUT", f"/expenses/{expense_id}", update_data, self.admin_token)
        
        if update_result.get("success"):
            updated_expense = update_result["data"]
            
            if updated_expense.get("expense_type") == "fijo":
                self.log_test("Update Expense Type", True, f"Expense type successfully updated from 'variable' to 'fijo'")
                
                # Verify the new fields were added
                if updated_expense.get("has_payment_reminder") is True:
                    self.log_test("Update Expense Fields", True, "Fijo-specific fields added successfully")
                else:
                    self.log_test("Update Expense Fields", False, "Fijo-specific fields not properly updated")
            else:
                self.log_test("Update Expense Type", False, f"Expense type not updated correctly: {updated_expense.get('expense_type')}")
        else:
            self.log_test("Update Expense Type", False, "Failed to update expense type", update_result)
    
    def test_delete_expenses_by_type(self):
        """Test deletion of expenses by type"""
        print("\n🗑️ Testing Expense Deletion by Type")
        
        # Get all expenses first
        expenses_result = self.make_request("GET", "/expenses", token=self.admin_token)
        
        if not expenses_result.get("success"):
            self.log_test("Get Expenses for Deletion", False, "Failed to get expenses", expenses_result)
            return
        
        expenses = expenses_result["data"]
        
        # Find expenses by type that we created in previous tests
        variable_expenses = [e for e in expenses if e.get("expense_type") == "variable" and "materiales" in e.get("description", "")]
        fijo_expenses = [e for e in expenses if e.get("expense_type") == "fijo" and "agua" in e.get("description", "")]
        unico_expenses = [e for e in expenses if e.get("expense_type") == "unico" and "escritorio" in e.get("description", "")]
        
        deletion_tests = [
            ("Variable", variable_expenses),
            ("Fijo", fijo_expenses),
            ("Unico", unico_expenses)
        ]
        
        for expense_type, expense_list in deletion_tests:
            if expense_list:
                expense_to_delete = expense_list[0]  # Take the first one
                expense_id = expense_to_delete["id"]
                
                delete_result = self.make_request("DELETE", f"/expenses/{expense_id}", token=self.admin_token)
                
                if delete_result.get("success"):
                    self.log_test(f"Delete {expense_type} Expense", True, f"{expense_type} expense deleted successfully")
                    
                    # Verify deletion
                    verify_result = self.make_request("GET", "/expenses", token=self.admin_token)
                    if verify_result.get("success"):
                        remaining_expenses = verify_result["data"]
                        still_exists = any(e.get("id") == expense_id for e in remaining_expenses)
                        
                        if not still_exists:
                            self.log_test(f"Verify {expense_type} Expense Deletion", True, f"{expense_type} expense successfully removed from list")
                        else:
                            self.log_test(f"Verify {expense_type} Expense Deletion", False, f"{expense_type} expense still appears in list")
                else:
                    self.log_test(f"Delete {expense_type} Expense", False, f"Failed to delete {expense_type} expense", delete_result)
            else:
                self.log_test(f"Find {expense_type} Expense for Deletion", False, f"No {expense_type} expense found for deletion test")
    
    def test_invoice_number_system_for_abonos(self):
        """Comprehensive testing of invoice number system for abonos"""
        print("\n🧾 Testing Invoice Number System for Abonos")
        
        # Step 1: Create test customer and reservation for testing
        print("   📋 Setting up test data...")
        
        # Create test customer
        customer_data = {
            "name": "Test Cliente Abonos",
            "phone": "809-555-9999",
            "email": "test.abonos@email.com",
            "address": "Santo Domingo, RD"
        }
        
        customer_result = self.make_request("POST", "/customers", customer_data, self.admin_token)
        if not customer_result.get("success"):
            self.log_test("Create Test Customer for Abonos", False, "Failed to create test customer", customer_result)
            return
        
        test_customer = customer_result["data"]
        self.log_test("Create Test Customer for Abonos", True, f"Created customer: {test_customer['name']}")
        
        # Get a villa for testing
        villas_result = self.make_request("GET", "/villas", token=self.admin_token)
        if not villas_result.get("success") or not villas_result["data"]:
            self.log_test("Get Villa for Abonos Test", False, "No villas available")
            return
        
        test_villa = villas_result["data"][0]
        
        # Create reservation with owner_price > 0 to auto-generate expense
        reservation_data = {
            "customer_id": test_customer["id"],
            "customer_name": test_customer["name"],
            "villa_id": test_villa["id"],
            "villa_code": test_villa["code"],
            "rental_type": "pasadia",
            "reservation_date": "2025-01-15T00:00:00Z",
            "check_in_time": "10:00 AM",
            "check_out_time": "8:00 PM",
            "guests": 6,
            "base_price": 20000.0,
            "owner_price": 12000.0,  # This will auto-generate an expense
            "subtotal": 20000.0,
            "total_amount": 20000.0,
            "amount_paid": 5000.0,
            "currency": "DOP",
            "status": "confirmed",
            "notes": "Test reservation for invoice number testing"
        }
        
        reservation_result = self.make_request("POST", "/reservations", reservation_data, self.admin_token)
        if not reservation_result.get("success"):
            self.log_test("Create Test Reservation", False, "Failed to create test reservation", reservation_result)
            return
        
        test_reservation = reservation_result["data"]
        self.log_test("Create Test Reservation", True, f"Created reservation #{test_reservation['invoice_number']}")
        
        # Find the auto-generated expense
        expenses_result = self.make_request("GET", "/expenses", token=self.admin_token)
        if not expenses_result.get("success"):
            self.log_test("Get Expenses for Abonos Test", False, "Failed to get expenses")
            return
        
        auto_expense = None
        for expense in expenses_result["data"]:
            if (expense.get("category") == "pago_propietario" and 
                expense.get("related_reservation_id") == test_reservation["id"]):
                auto_expense = expense
                break
        
        if not auto_expense:
            self.log_test("Find Auto-Generated Expense", False, "Auto-generated expense not found")
            return
        
        self.log_test("Find Auto-Generated Expense", True, f"Found auto-generated expense: {auto_expense['id']}")
        
        # TEST 1.1: Employee creates abono with auto-generated invoice_number (reservation)
        print("\n   🧾 Test 1.1: Employee abono with auto-generated invoice_number (reservation)")
        
        abono_data_employee = {
            "amount": 1000.0,
            "currency": "DOP",
            "payment_method": "efectivo",
            "payment_date": "2025-01-15T10:00:00Z",
            "notes": "Primer abono - auto-generado"
        }
        
        abono_result = self.make_request("POST", f"/reservations/{test_reservation['id']}/abonos", 
                                       abono_data_employee, self.employee_token)
        
        if abono_result.get("success"):
            created_abono = abono_result["data"]
            if created_abono.get("invoice_number"):
                self.log_test("Employee Abono Auto-Generated Invoice (Reservation)", True, 
                             f"Employee abono created with auto-generated invoice_number: {created_abono['invoice_number']}")
                employee_invoice_num = created_abono["invoice_number"]
            else:
                self.log_test("Employee Abono Auto-Generated Invoice (Reservation)", False, 
                             "Employee abono missing invoice_number")
                return
        else:
            self.log_test("Employee Abono Auto-Generated Invoice (Reservation)", False, 
                         "Failed to create employee abono", abono_result)
            return
        
        # Verify abono appears in reservation abonos list
        abonos_result = self.make_request("GET", f"/reservations/{test_reservation['id']}/abonos", 
                                        token=self.employee_token)
        
        if abonos_result.get("success"):
            abonos = abonos_result["data"]
            found_abono = any(a.get("invoice_number") == employee_invoice_num for a in abonos)
            if found_abono:
                self.log_test("Verify Employee Abono in List (Reservation)", True, 
                             f"Employee abono with invoice_number {employee_invoice_num} found in list")
            else:
                self.log_test("Verify Employee Abono in List (Reservation)", False, 
                             "Employee abono not found in reservation abonos list")
        else:
            self.log_test("Get Reservation Abonos", False, "Failed to get reservation abonos", abonos_result)
        
        # TEST 1.2: Admin creates abono with manual invoice_number (reservation)
        print("\n   🧾 Test 1.2: Admin abono with manual invoice_number (reservation)")
        
        manual_invoice_num = "9999"
        abono_data_admin = {
            "amount": 500.0,
            "currency": "DOP",
            "payment_method": "transferencia",
            "payment_date": "2025-01-16T10:00:00Z",
            "notes": "Segundo abono - número manual",
            "invoice_number": manual_invoice_num
        }
        
        admin_abono_result = self.make_request("POST", f"/reservations/{test_reservation['id']}/abonos", 
                                             abono_data_admin, self.admin_token)
        
        if admin_abono_result.get("success"):
            admin_abono = admin_abono_result["data"]
            if admin_abono.get("invoice_number") == manual_invoice_num:
                self.log_test("Admin Manual Invoice Number (Reservation)", True, 
                             f"Admin abono created with manual invoice_number: {manual_invoice_num}")
            else:
                self.log_test("Admin Manual Invoice Number (Reservation)", False, 
                             f"Admin abono has wrong invoice_number: {admin_abono.get('invoice_number')}")
        else:
            self.log_test("Admin Manual Invoice Number (Reservation)", False, 
                         "Failed to create admin abono with manual invoice_number", admin_abono_result)
        
        # TEST 1.3: Try to create duplicate invoice_number (should fail)
        print("\n   🧾 Test 1.3: Duplicate invoice_number validation (reservation)")
        
        duplicate_abono_data = {
            "amount": 300.0,
            "currency": "DOP",
            "payment_method": "efectivo",
            "payment_date": "2025-01-17T10:00:00Z",
            "notes": "Intento de duplicado",
            "invoice_number": manual_invoice_num  # Same as previous
        }
        
        duplicate_result = self.make_request("POST", f"/reservations/{test_reservation['id']}/abonos", 
                                           duplicate_abono_data, self.admin_token)
        
        if duplicate_result.get("status_code") == 400:
            error_message = duplicate_result.get("data", {}).get("detail", "")
            if "already in use" in error_message or "ya existe" in error_message:
                self.log_test("Duplicate Invoice Number Validation (Reservation)", True, 
                             f"Duplicate invoice_number correctly rejected: {error_message}")
            else:
                self.log_test("Duplicate Invoice Number Validation (Reservation)", False, 
                             f"Wrong error message: {error_message}")
        else:
            self.log_test("Duplicate Invoice Number Validation (Reservation)", False, 
                         f"Duplicate invoice_number not rejected. Status: {duplicate_result.get('status_code')}")
        
        # TEST 1.4: Employee cannot specify manual invoice_number
        print("\n   🧾 Test 1.4: Employee forbidden from manual invoice_number (reservation)")
        
        employee_manual_data = {
            "amount": 200.0,
            "currency": "DOP",
            "payment_method": "efectivo",
            "payment_date": "2025-01-18T10:00:00Z",
            "notes": "Empleado intenta número manual",
            "invoice_number": "8888"
        }
        
        employee_manual_result = self.make_request("POST", f"/reservations/{test_reservation['id']}/abonos", 
                                                 employee_manual_data, self.employee_token)
        
        if employee_manual_result.get("status_code") == 403:
            self.log_test("Employee Manual Invoice Forbidden (Reservation)", True, 
                         "Employee correctly forbidden from specifying manual invoice_number")
        else:
            self.log_test("Employee Manual Invoice Forbidden (Reservation)", False, 
                         f"Employee manual invoice_number not properly forbidden. Status: {employee_manual_result.get('status_code')}")
        
        # TEST 2: EXPENSE ABONOS TESTING
        print("\n   💰 Testing Invoice Numbers for Expense Abonos")
        
        # TEST 2.1: Employee creates abono with auto-generated invoice_number (expense)
        print("\n   🧾 Test 2.1: Employee abono with auto-generated invoice_number (expense)")
        
        expense_abono_employee = {
            "amount": 2000.0,
            "currency": "DOP",
            "payment_method": "efectivo",
            "payment_date": "2025-01-19T10:00:00Z",
            "notes": "Abono a gasto - auto-generado"
        }
        
        expense_abono_result = self.make_request("POST", f"/expenses/{auto_expense['id']}/abonos", 
                                               expense_abono_employee, self.employee_token)
        
        if expense_abono_result.get("success"):
            expense_abono = expense_abono_result["data"]
            if expense_abono.get("invoice_number"):
                self.log_test("Employee Abono Auto-Generated Invoice (Expense)", True, 
                             f"Employee expense abono created with auto-generated invoice_number: {expense_abono['invoice_number']}")
                expense_employee_invoice = expense_abono["invoice_number"]
            else:
                self.log_test("Employee Abono Auto-Generated Invoice (Expense)", False, 
                             "Employee expense abono missing invoice_number")
        else:
            self.log_test("Employee Abono Auto-Generated Invoice (Expense)", False, 
                         "Failed to create employee expense abono", expense_abono_result)
        
        # TEST 2.2: Admin creates abono with manual invoice_number (expense)
        print("\n   🧾 Test 2.2: Admin abono with manual invoice_number (expense)")
        
        manual_expense_invoice = "7777"
        expense_abono_admin = {
            "amount": 1500.0,
            "currency": "DOP",
            "payment_method": "transferencia",
            "payment_date": "2025-01-20T10:00:00Z",
            "notes": "Abono a gasto - número manual",
            "invoice_number": manual_expense_invoice
        }
        
        admin_expense_abono_result = self.make_request("POST", f"/expenses/{auto_expense['id']}/abonos", 
                                                     expense_abono_admin, self.admin_token)
        
        if admin_expense_abono_result.get("success"):
            admin_expense_abono = admin_expense_abono_result["data"]
            if admin_expense_abono.get("invoice_number") == manual_expense_invoice:
                self.log_test("Admin Manual Invoice Number (Expense)", True, 
                             f"Admin expense abono created with manual invoice_number: {manual_expense_invoice}")
            else:
                self.log_test("Admin Manual Invoice Number (Expense)", False, 
                             f"Admin expense abono has wrong invoice_number: {admin_expense_abono.get('invoice_number')}")
        else:
            self.log_test("Admin Manual Invoice Number (Expense)", False, 
                         "Failed to create admin expense abono with manual invoice_number", admin_expense_abono_result)
        
        # TEST 2.3: Cross-collection validation (use reservation invoice_number in expense abono)
        print("\n   🧾 Test 2.3: Cross-collection duplicate validation")
        
        cross_duplicate_data = {
            "amount": 800.0,
            "currency": "DOP",
            "payment_method": "efectivo",
            "payment_date": "2025-01-21T10:00:00Z",
            "notes": "Intento usar número de reservación",
            "invoice_number": manual_invoice_num  # Use the reservation invoice number
        }
        
        cross_duplicate_result = self.make_request("POST", f"/expenses/{auto_expense['id']}/abonos", 
                                                 cross_duplicate_data, self.admin_token)
        
        if cross_duplicate_result.get("status_code") == 400:
            error_message = cross_duplicate_result.get("data", {}).get("detail", "")
            if "already in use" in error_message or "ya existe" in error_message:
                self.log_test("Cross-Collection Duplicate Validation", True, 
                             f"Cross-collection duplicate correctly rejected: {error_message}")
            else:
                self.log_test("Cross-Collection Duplicate Validation", False, 
                             f"Wrong error message for cross-collection duplicate: {error_message}")
        else:
            self.log_test("Cross-Collection Duplicate Validation", False, 
                         f"Cross-collection duplicate not rejected. Status: {cross_duplicate_result.get('status_code')}")
        
        # TEST 3: Verify get_next_invoice_number avoids duplicates
        print("\n   🧾 Test 3: Verify unique auto-generated invoice numbers")
        
        # Create multiple abonos without specifying invoice_number
        auto_generated_numbers = []
        
        for i in range(3):
            auto_abono_data = {
                "amount": 100.0 + (i * 50),
                "currency": "DOP",
                "payment_method": "efectivo",
                "payment_date": f"2025-01-{22+i}T10:00:00Z",
                "notes": f"Auto abono #{i+1}"
            }
            
            auto_result = self.make_request("POST", f"/reservations/{test_reservation['id']}/abonos", 
                                          auto_abono_data, self.employee_token)
            
            if auto_result.get("success"):
                auto_abono = auto_result["data"]
                invoice_num = auto_abono.get("invoice_number")
                if invoice_num:
                    auto_generated_numbers.append(invoice_num)
        
        # Check if all numbers are unique
        if len(auto_generated_numbers) == 3:
            unique_numbers = set(auto_generated_numbers)
            if len(unique_numbers) == 3:
                self.log_test("Unique Auto-Generated Numbers", True, 
                             f"All auto-generated numbers are unique: {auto_generated_numbers}")
                
                # Check if numbers are consecutive (they should be)
                sorted_numbers = sorted([int(num) for num in auto_generated_numbers])
                is_consecutive = all(sorted_numbers[i] == sorted_numbers[i-1] + 1 for i in range(1, len(sorted_numbers)))
                
                if is_consecutive:
                    self.log_test("Consecutive Invoice Numbers", True, 
                                 f"Auto-generated numbers are consecutive: {sorted_numbers}")
                else:
                    self.log_test("Consecutive Invoice Numbers", False, 
                                 f"Auto-generated numbers are not consecutive: {sorted_numbers}")
            else:
                self.log_test("Unique Auto-Generated Numbers", False, 
                             f"Duplicate auto-generated numbers found: {auto_generated_numbers}")
        else:
            self.log_test("Create Multiple Auto Abonos", False, 
                         f"Failed to create 3 auto abonos. Created: {len(auto_generated_numbers)}")
        
        # FINAL VERIFICATION: Get all abonos and verify invoice_number presence
        print("\n   🧾 Final Verification: All abonos have invoice_number")
        
        # Get reservation abonos
        final_res_abonos = self.make_request("GET", f"/reservations/{test_reservation['id']}/abonos", 
                                           token=self.admin_token)
        
        if final_res_abonos.get("success"):
            res_abonos = final_res_abonos["data"]
            abonos_with_invoice = [a for a in res_abonos if a.get("invoice_number")]
            
            if len(abonos_with_invoice) == len(res_abonos):
                self.log_test("All Reservation Abonos Have Invoice Numbers", True, 
                             f"All {len(res_abonos)} reservation abonos have invoice_number")
            else:
                self.log_test("All Reservation Abonos Have Invoice Numbers", False, 
                             f"Only {len(abonos_with_invoice)}/{len(res_abonos)} reservation abonos have invoice_number")
        
        # Get expense abonos
        final_exp_abonos = self.make_request("GET", f"/expenses/{auto_expense['id']}/abonos", 
                                           token=self.admin_token)
        
        if final_exp_abonos.get("success"):
            exp_abonos = final_exp_abonos["data"]
            exp_abonos_with_invoice = [a for a in exp_abonos if a.get("invoice_number")]
            
            if len(exp_abonos_with_invoice) == len(exp_abonos):
                self.log_test("All Expense Abonos Have Invoice Numbers", True, 
                             f"All {len(exp_abonos)} expense abonos have invoice_number")
            else:
                self.log_test("All Expense Abonos Have Invoice Numbers", False, 
                             f"Only {len(exp_abonos_with_invoice)}/{len(exp_abonos)} expense abonos have invoice_number")
        
        print(f"\n   🎯 INVOICE NUMBER SYSTEM TEST SUMMARY COMPLETE")
        
        # Summary of what was tested
        print("   ✅ Tested Features:")
        print("      - Auto-generation of invoice_number for employee abonos")
        print("      - Manual invoice_number specification for admin abonos")
        print("      - Duplicate invoice_number validation (400 error)")
        print("      - Employee forbidden from manual invoice_number (403 error)")
        print("      - Cross-collection duplicate validation")
        print("      - Unique and consecutive auto-generated numbers")
        print("      - Invoice_number presence in all abonos")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend Testing Suite for Category System")
        print("=" * 60)
        
        # Health check
        self.test_health_check()
        
        # Auth and setup
        print("\n📝 Auth & Setup Tests")
        self.test_register_admin()
        self.test_register_employee()
        self.test_admin_login()
        self.test_employee_login()
        
        # Category tests (admin)
        print("\n🏷️ Category Tests (Admin)")
        self.test_create_categories_admin()
        self.test_get_categories_admin()
        self.test_update_category_admin()
        self.test_get_single_category_admin()
        
        # Villa tests
        print("\n🏠 Villa Tests")
        self.test_create_villas_with_categories()
        self.test_get_all_villas()
        self.test_search_villas()
        self.test_filter_villas_by_category()
        
        # Category deletion
        print("\n🗑️ Category Deletion Tests")
        self.test_delete_category_and_unassign_villas()
        
        # Employee permissions
        print("\n👤 Employee Permission Tests")
        self.test_employee_permissions()
        
        # Auto-expense creation flow
        print("\n💰 Auto-Expense Creation Tests")
        self.test_auto_expense_creation_flow()
        
        # NEW FUNCTIONALITY TESTS
        print("\n🆕 New Functionality Tests")
        self.test_customer_dni_field()
        self.test_auto_generated_expense_deletion()
        
        # EXPENSE TYPE SYSTEM TESTS
        print("\n💸 Expense Type System Tests")
        self.test_existing_expenses_with_types()
        self.test_create_variable_expense()
        self.test_create_fijo_expense()
        self.test_create_unico_expense()
        self.test_update_expense_type()
        self.test_delete_expenses_by_type()
        
        # INVOICE NUMBER SYSTEM TESTS FOR ABONOS
        print("\n🧾 Invoice Number System Tests for Abonos")
        self.test_invoice_number_system_for_abonos()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)