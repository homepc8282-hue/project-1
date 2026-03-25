from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from datetime import datetime
from kivy.graphics import Color



Window.clearcolor = (0.93, 0.97, 1, 1)

# ----------------------------
# GLOBAL DATA
# ----------------------------
admin = {"username": "owner", "password": "admin123"}

companies = {
    "ferozons": {"pwd": "com123", "name": "Ferozsons Labs", "verified": True}
}

pharmacy_requests = []
approved_pharmacies = {}

products = []
orders = []
cart = []

current_user = None
user_role = None


# ----------------------------
# POPUP MESSAGE
# ----------------------------
def msg(title, text):
    Popup(title=title, content=Label(text=text), size_hint=(0.6, 0.3)).open()


# ----------------------------
# LOGIN SCREEN
# ----------------------------
class Login(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=40, spacing=15)
        b.add_widget(Label(text="PHARMA DISTRIBUTION", font_size=24, bold=True, color=(0, 0.2, 0.4, 1)))

        self.user = TextInput(hint_text="Username", size_hint_y=None, height=48)
        self.pwd = TextInput(hint_text="Password", password=True, size_hint_y=None, height=48)

        login_btn = Button(text="LOGIN", size_hint_y=None, height=50, background_color=(0.1, 0.3, 0.6, 1))
        reg_btn = Button(text="REGISTER PHARMACY", size_hint_y=None, height=45)

        login_btn.bind(on_press=self.check)
        reg_btn.bind(on_press=self.go_register)

        b.add_widget(self.user)
        b.add_widget(self.pwd)
        b.add_widget(login_btn)
        b.add_widget(reg_btn)
        self.add_widget(b)

    def go_register(self, x):
        self.manager.current = 'pharmacy_register'

    def check(self, x):
        global current_user, user_role
        u = self.user.text.strip()
        p = self.pwd.text.strip()

        # Admin login
        if u == admin['username'] and p == admin['password']:
            current_user = u
            user_role = 'admin'
            self.manager.current = 'admin_dash'
            return

        # Company login
        if u in companies:
            if companies[u]['pwd'] == p:
                current_user = u
                user_role = 'company'
                self.manager.current = 'company_dash'
                return

        # Approved Pharmacy login (this is the critical part!)
        if u in approved_pharmacies:
            if approved_pharmacies[u]['pwd'] == p:
                current_user = u
                user_role = 'pharmacy'
                self.manager.current = 'pharmacy_dash'  # Exact screen name
                return

        # Fallback error message
        msg("Login Error", "Invalid credentials OR pharmacy not approved by admin")


# ----------------------------
# PHARMACY REGISTRATION SCREEN
# ----------------------------
class PharmacyRegister(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=30, spacing=12)
        b.add_widget(Label(text="Pharmacy Registration", font_size=20, bold=True))

        self.shop = TextInput(hint_text="Shop Name", size_hint_y=None, height=40)
        self.owner = TextInput(hint_text="Owner Name", size_hint_y=None, height=40)
        self.phone = TextInput(hint_text="Phone", size_hint_y=None, height=40)
        self.user = TextInput(hint_text="Create Username", size_hint_y=None, height=40)
        self.pwd = TextInput(hint_text="Password", password=True, size_hint_y=None, height=40)

        sub = Button(text="Submit Request", size_hint_y=None, height=48, background_color=(0.0, 0.5, 0.3, 1))
        back = Button(text="Back", size_hint_y=None, height=40)

        sub.bind(on_press=self.send)
        back.bind(on_press=self.go_back)

        b.add_widget(self.shop)
        b.add_widget(self.owner)
        b.add_widget(self.phone)
        b.add_widget(self.user)
        b.add_widget(self.pwd)
        b.add_widget(sub)
        b.add_widget(back)
        self.add_widget(b)

    def go_back(self, x):
        self.manager.current = 'login'

    def send(self, x):
        data = {
            "user": self.user.text.strip(),
            "pwd": self.pwd.text.strip(),
            "shop": self.shop.text.strip(),
            "owner": self.owner.text.strip(),
            "phone": self.phone.text.strip()
        }
        if all([data["user"], data["pwd"], data["shop"]]):
            pharmacy_requests.append(data)
            msg("Sent", "Your request sent for approval")
            self.manager.current = 'login'
        else:
            msg("Empty", "Fill all required fields")


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
class AdminDash(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=25, spacing=14)
        b.add_widget(Label(text="Admin Panel", font_size=22, bold=True))

        rq = Button(text="View Pharmacy Requests", size_hint_y=None, height=55, bold=True)
        com = Button(text="Add Company Account", size_hint_y=None, height=55, bold=True)
        lo = Button(text="Logout", size_hint_y=None, height=55, bold=True, background_color=(0.7, 0.2, 0.2, 1))

        rq.bind(on_press=self.go_requests)
        com.bind(on_press=self.go_add_company)
        lo.bind(on_press=self.out)

        b.add_widget(rq)
        b.add_widget(com)
        b.add_widget(lo)
        self.add_widget(b)

    def go_requests(self, x):
        self.manager.current = 'admin_requests'

    def go_add_company(self, x):
        self.manager.current = 'add_company'

    def out(self, x):
        global current_user, user_role
        current_user = user_role = None
        self.manager.current = 'login'


# ----------------------------
# ADMIN: ADD COMPANY
# ----------------------------
class AddCompany(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=30, spacing=12)
        self.u = TextInput(hint_text="Company Username", size_hint_y=None, height=40)
        self.p = TextInput(hint_text="Password", password=True, size_hint_y=None, height=40)
        self.n = TextInput(hint_text="Company Full Name", size_hint_y=None, height=40)

        save = Button(text="Add Company", size_hint_y=None, height=48)
        back = Button(text="Back", size_hint_y=None, height=40)

        save.bind(on_press=self.add)
        back.bind(on_press=self.go_back)

        b.add_widget(self.u)
        b.add_widget(self.p)
        b.add_widget(self.n)
        b.add_widget(save)
        b.add_widget(back)
        self.add_widget(b)

    def go_back(self, x):
        self.manager.current = 'admin_dash'

    def add(self, x):
        uname = self.u.text.strip()
        pwd = self.p.text.strip()
        name = self.n.text.strip()
        if uname and pwd:
            companies[uname] = {"pwd": pwd, "name": name, "verified": True}
            msg("Success", "Company added")
            self.manager.current = 'admin_dash'
        else:
            msg("Error", "Fill username & password")


# ----------------------------
# ADMIN: PHARMACY REQUESTS
# ----------------------------
class AdminRequests(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical')

        top = BoxLayout(size_hint_y=None, height=50)
        top.add_widget(Label(text="Pharmacy Approval Requests", bold=True, font_size=18))
        back_btn = Button(text="Back", size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        top.add_widget(back_btn)

        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        self.box.bind(minimum_height=self.box.setter('height'))
        sc = ScrollView()
        sc.add_widget(self.box)

        self.main.add_widget(top)
        self.main.add_widget(sc)
        self.add_widget(self.main)

    def go_back(self, x):
        self.manager.current = 'admin_dash'

    def on_enter(self):
        self.box.clear_widgets()

        if not pharmacy_requests:
            self.box.add_widget(Label(text="No pending requests", size_hint_y=None, height=40))
            return

        for idx, req in enumerate(pharmacy_requests):
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=120)

            # ✅ ONLY TEXT COLOR CHANGED HERE (black)
            card.add_widget(Label(text=f"Username: {req['user']}", color=(0, 0, 0, 1)))
            card.add_widget(Label(text=f"Shop: {req['shop']}", color=(0, 0, 0, 1)))
            card.add_widget(Label(text=f"Owner: {req['owner']}", color=(0, 0, 0, 1)))
            card.add_widget(Label(text=f"Phone: {req['phone']}", color=(0, 0, 0, 1)))

            btn = Button(text="Approve", size_hint_y=None, height=40, background_color=(0, 0.6, 0, 1))

            def approve_click(instance, i=idx):
                data = pharmacy_requests.pop(i)
                approved_pharmacies[data['user']] = data
                self.on_enter()
                msg("Approved", "Pharmacy activated")

            btn.bind(on_press=approve_click)

            card.add_widget(btn)
            self.box.add_widget(card)


# ----------------------------
# COMPANY DASHBOARD
# ----------------------------
class CompanyDash(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=25, spacing=14)
        b.add_widget(Label(text="Company Panel", font_size=22, bold=True))

        addp = Button(text="Add New Product", size_hint_y=None, height=55)
        viewp = Button(text="My Products", size_hint_y=None, height=55)
        lo = Button(text="Logout", size_hint_y=None, height=55, background_color=(0.7, 0.2, 0.2, 1))

        addp.bind(on_press=self.go_add_product)
        viewp.bind(on_press=self.go_products)
        lo.bind(on_press=self.out)

        b.add_widget(addp)
        b.add_widget(viewp)
        b.add_widget(lo)
        self.add_widget(b)

    def go_add_product(self, x):
        self.manager.current = 'add_product'

    def go_products(self, x):
        self.manager.current = 'company_products'

    def out(self, x):
        global current_user, user_role
        current_user = user_role = None
        self.manager.current = 'login'


# ----------------------------
# COMPANY: ADD PRODUCT
# ----------------------------
class AddProduct(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        b = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.med_name = TextInput(hint_text="Medicine Name", size_hint_y=None, height=40)
        self.desc = TextInput(hint_text="Description", size_hint_y=None, height=40)
        self.price = TextInput(hint_text="Price (PKR)", input_filter='int', size_hint_y=None, height=40)
        self.var = TextInput(hint_text="Variant (e.g. 500mg, 100ml)", size_hint_y=None, height=40)
        self.rate = TextInput(hint_text="Rating (1-5)", input_filter='int', size_hint_y=None, height=40)

        save = Button(text="Save Product", size_hint_y=None, height=48)
        back = Button(text="Back", size_hint_y=None, height=40)

        save.bind(on_press=self.save)
        back.bind(on_press=self.go_back)

        b.add_widget(self.med_name)
        b.add_widget(self.desc)
        b.add_widget(self.price)
        b.add_widget(self.var)
        b.add_widget(self.rate)
        b.add_widget(save)
        b.add_widget(back)
        self.add_widget(b)

    def go_back(self, x):
        self.manager.current = 'company_dash'

    def save(self, x):
        try:
            name = self.med_name.text.strip()
            price = int(self.price.text.strip()) if self.price.text.strip() else 0
            rt = int(self.rate.text.strip()) if self.rate.text.strip() else 3

            if not name or price <= 0:
                msg("Error", "Enter valid name & price")
                return

            products.append({
                "company": current_user,
                "name": name,
                "desc": self.desc.text.strip(),
                "price": price,
                "var": self.var.text.strip(),
                "rating": max(1, min(5, rt))
            })
            msg("Done", "Product added")
            self.manager.current = 'company_dash'
        except:
            msg("Error", "Enter valid numbers")


# ----------------------------
# COMPANY: VIEW PRODUCTS
# ----------------------------
class CompanyProducts(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical')
        self.main.canvas.before.clear()
        with self.main.canvas.before:
            Color(0.94, 0.97, 1, 1)  # soft light blue background

        top = BoxLayout(size_hint_y=None, height=50)
        top.add_widget(Label(text="My Products", bold=True, font_size=20))
        back_btn = Button(text="Back", size_hint_x=0.2, background_color=(0.2, 0.6, 0.8, 1))
        back_btn.bind(on_press=self.go_back)
        top.add_widget(back_btn)

        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.box.bind(minimum_height=self.box.setter('height'))
        sc = ScrollView()
        sc.add_widget(self.box)

        self.main.add_widget(top)
        self.main.add_widget(sc)
        self.add_widget(self.main)

    def go_back(self, instance):
        self.manager.current = 'company_dash'

    def on_enter(self):
        self.box.clear_widgets()
        if not products:
            self.box.add_widget(Label(text="No products added yet!", size_hint_y=None, height=40, color=(0,0,0,1)))
            return

        for product in products:
            if product['company'] == current_user:
                row = BoxLayout(size_hint_y=None, height=50)
                row.add_widget(Label(text=product['name'], size_hint_x=0.4, font_size=16, color=(0,0,0,1)))
                row.add_widget(Label(text=f"Variant: {product['var']}", size_hint_x=0.3, font_size=14, color=(0,0,0,1)))
                row.add_widget(Label(text=f"Rs. {product['price']}", size_hint_x=0.3, font_size=16, color=(0.1, 0.6, 0.2, 1)))
                self.box.add_widget(row)

# ----------------------------
# PHARMACY DASHBOARD
# ----------------------------
class PharmacyDash(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical', padding=25, spacing=14)
        self.main.canvas.before.clear()
        with self.main.canvas.before:
            Color(0.94, 0.97, 1, 1)

        self.main.add_widget(Label(text="Pharmacy Panel", font_size=22, bold=True, color=(0,0,0,1)))

        b1 = Button(text="Browse Products", size_hint_y=None, height=55)
        b2 = Button(text="My Cart", size_hint_y=None, height=55)
        b3 = Button(text="My Orders", size_hint_y=None, height=55)
        b4 = Button(text="Logout", size_hint_y=None, height=55, background_color=(0.7, 0, 0, 1))

        b1.bind(on_press=self.go_browse)
        b2.bind(on_press=self.go_cart)
        b3.bind(on_press=self.go_orders)
        b4.bind(on_press=self.out)

        self.main.add_widget(b1)
        self.main.add_widget(b2)
        self.main.add_widget(b3)
        self.main.add_widget(b4)
        self.add_widget(self.main)

    def go_browse(self, x):
        self.manager.current = 'browse'
    def go_cart(self, x):
        self.manager.current = 'cart'
    def go_orders(self, x):
        self.manager.current = 'pharma_orders'
    def out(self, x):
        global current_user, user_role
        current_user = user_role = None
        self.manager.current = 'login'


# ----------------------------
# PHARMACY: BROWSE PRODUCTS
# ----------------------------
class Browse(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical')
        self.main.canvas.before.clear()
        with self.main.canvas.before:
            Color(0.94, 0.97, 1, 1)

        top = BoxLayout(size_hint_y=None, height=50)
        top.add_widget(Label(text="All Products", bold=True, font_size=20, color=(0,0,0,1)))
        back = Button(text="Back", size_hint_x=0.2)
        back.bind(on_press=self.go_back)
        top.add_widget(back)

        self.box = BoxLayout(size_hint_y=None, spacing=12, padding=10)
        self.box.bind(minimum_height=self.box.setter('height'))
        sc = ScrollView()
        sc.add_widget(self.box)

        self.main.add_widget(top)
        self.main.add_widget(sc)
        self.add_widget(self.main)

    def go_back(self, x):
        self.manager.current = 'pharmacy_dash'

    def on_enter(self):
        self.box.clear_widgets()
        for prod in products:
            b = BoxLayout(size_hint_y=None, height=160, orientation='vertical')
            b.add_widget(Label(text=f"[b]{prod['name']}[/b]", markup=True, font_size=16, color=(0,0,0,1)))
            b.add_widget(Label(text=f"Variant: {prod['var']}", color=(0,0,0,1)))
            b.add_widget(Label(text=f"Price: Rs. {prod['price']}", color=(0,0,0,1)))

            qty_row = BoxLayout(size_hint_y=None, height=35)
            qty_row.add_widget(Label(text="Qty:", color=(0,0,0,1)))
            qty_input = TextInput(text="1", input_filter='int', size_hint_x=0.3)
            qty_row.add_widget(qty_input)
            atc = Button(text="Add to Cart", size_hint_x=0.5)

            def add_click(instance, p=prod, q=qty_input):
                try:
                    qty = int(q.text)
                except:
                    qty = 1
                for item in cart:
                    if item['product'] == p:
                        item['qty'] += qty
                        msg("Updated", "Quantity updated")
                        return
                cart.append({"product": p, "qty": qty})
                msg("Added", f"{p['name']} x{qty} added to cart")

            atc.bind(on_press=add_click)
            qty_row.add_widget(atc)
            b.add_widget(qty_row)
            self.box.add_widget(b)


# ----------------------------
# PHARMACY: CART & CHECKOUT
# ----------------------------
class Cart(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical')
        self.main.canvas.before.clear()
        with self.main.canvas.before:
            Color(0.94, 0.97, 1, 1)

        top = BoxLayout(size_hint_y=None, height=50)
        top.add_widget(Label(text="My Cart", bold=True, font_size=20, color=(0, 0, 0, 1)))
        back = Button(text="Back", size_hint_x=0.2)
        back.bind(on_press=self.go_back)
        top.add_widget(back)

        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.box.bind(minimum_height=self.box.setter('height'))
        sc = ScrollView()
        sc.add_widget(self.box)

        # Payment method
        pay_layout = BoxLayout(size_hint_y=None, height=40)
        pay_layout.add_widget(Label(text="Payment:", color=(0, 0, 0, 1)))
        self.payment = Spinner(text='COD', values=('COD', 'Jazzcash', 'Easypaisa'), size_hint_x=0.4)
        pay_layout.add_widget(self.payment)

        self.total_label = Label(text="Total: Rs. 0", bold=True, size_hint_y=None, height=40, color=(0, 0, 0, 1))
        order_btn = Button(text="Place Order", size_hint_y=None, height=50, background_color=(0, 0.6, 0, 1))
        order_btn.bind(on_press=self.place_order)

        self.main.add_widget(top)
        self.main.add_widget(sc)
        self.main.add_widget(pay_layout)
        self.main.add_widget(self.total_label)
        self.main.add_widget(order_btn)
        self.add_widget(self.main)

    def go_back(self, x):
        self.manager.current = 'pharmacy_dash'

    def on_enter(self):
        self.box.clear_widgets()
        total = 0
        for index, item in enumerate(cart):
            p = item['product']
            qty = item['qty']
            subtotal = p['price'] * qty
            total += subtotal

            row = BoxLayout(size_hint_y=None, height=50)
            row.add_widget(Label(text=p['name'], size_hint_x=0.3, color=(0, 0, 0, 1)))
            row.add_widget(Label(text=f"x{qty}", size_hint_x=0.2, color=(0, 0, 0, 1)))
            row.add_widget(Label(text=f"Rs. {subtotal}", size_hint_x=0.3, color=(0, 0, 0, 1)))

            # ✅ REMOVE BUTTON FOR EACH PRODUCT
            remove_btn = Button(text="Remove", size_hint_x=0.2, background_color=(0.8, 0, 0, 1))

            def remove_action(instance, idx=index):
                cart.pop(idx)
                self.on_enter()

            remove_btn.bind(on_press=remove_action)
            row.add_widget(remove_btn)

            self.box.add_widget(row)

        self.total_label.text = f"Total: Rs. {total}"

    def place_order(self, x):
        if not cart:
            msg("Cart Empty", "Add products first")
            return

        orders.append({
            "pharmacy": current_user,
            "items": cart.copy(),
            "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "payment": self.payment.text
        })
        cart.clear()
        msg("Order Placed", f"Via {self.payment.text}")
        self.manager.current = 'pharmacy_dash'



# ----------------------------
# PHARMACY: VIEW ORDERS
# ----------------------------
class PharmaOrders(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.main = BoxLayout(orientation='vertical')
        self.main.canvas.before.clear()
        with self.main.canvas.before:
            Color(0.94, 0.97, 1, 1)

        top = BoxLayout(size_hint_y=None, height=50)
        top.add_widget(Label(text="My Orders", bold=True, font_size=20, color=(0,0,0,1)))
        back = Button(text="Back", size_hint_x=0.2)
        back.bind(on_press=self.go_back)
        top.add_widget(back)

        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.box.bind(minimum_height=self.box.setter('height'))
        sc = ScrollView()
        sc.add_widget(self.box)

        self.main.add_widget(top)
        self.main.add_widget(sc)
        self.add_widget(self.main)

    def go_back(self, x):
        self.manager.current = 'pharmacy_dash'

    def on_enter(self):
        self.box.clear_widgets()
        for order in orders:
            if order['pharmacy'] == current_user:
                self.box.add_widget(Label(
                    text=f"Order: {order['date']}", bold=True, size_hint_y=None, height=30, color=(0,0,0,1)
                ))
                for item in order['items']:
                    prod = item['product']
                    qty = item['qty']
                    self.box.add_widget(Label(
                        text=f"→ {prod['name']} x{qty} = Rs {prod['price']*qty}",
                        size_hint_y=None, height=26, color=(0,0,0,1)
                    ))
                self.box.add_widget(Label(text="────────────────────", size_hint_y=None, height=15, color=(0,0,0,1)))

# ----------------------------
# SCREEN MANAGER
# ----------------------------
class Manager(ScreenManager):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Add all your screens here
        self.add_widget(Login(name="login"))
        self.add_widget(PharmacyRegister(name="pharmacy_register"))
        self.add_widget(AdminDash(name="admin_dash"))
        self.add_widget(AddCompany(name="add_company"))
        self.add_widget(AdminRequests(name="admin_requests"))
        self.add_widget(CompanyDash(name="company_dash"))
        self.add_widget(AddProduct(name="add_product"))
        self.add_widget(CompanyProducts(name="company_products"))
        self.add_widget(Browse(name="browse"))
        self.add_widget(Cart(name="cart"))
        self.add_widget(PharmaOrders(name="pharma_orders"))
        self.add_widget(PharmacyDash(name="pharmacy_dash"))  # ✅ Critical missing screen


# ----------------------------
# MAIN APP
# ----------------------------
class PharmaApp(App):
    def build(self):
        return Manager()


if __name__ == "__main__":
    PharmaApp().run()