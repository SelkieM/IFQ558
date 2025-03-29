from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Book, Order, Cart, OrderForm
from . import db


# create blueprint
views = Blueprint('views', __name__)


# ROUTES


# route to home page
@views.route("/")
def home():
    # return index.html page
    return render_template("index.html")


# route to view new books page and pass in all books from database
@views.route('/newBooks')
def newBooks():
    # query all books from database
    books = Book.query.all()
    # return new_books.html page and pass in books
    return render_template('new_books.html', books=books)


# add new book route
@views.route('/add_book', methods=['GET', 'POST'])
def add_new_book():
    # handle POST request of adding new book
    if request.method == 'POST':
        # get data from form
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['category']
        image = request.form['image']
        # create new book object
        new_book = Book(name=name, price=price,
                        description=description, category=category, image=image)
        # add new book to database
        db.session.add(new_book)
        db.session.commit()
        # return to books page
        return redirect(url_for('views.newBooks'))
    # return add_book.html page
    return render_template('add_book.html')


# update book route
@views.route("/updateBook", methods=['GET', 'POST'])
def updateBook():
    # get book id from request
    book_id = request.args.get('book_id')
    # get book object
    book = Book.query.filter_by(id=book_id).first()
    if request.method == 'POST':
        # get book data from form
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['category']
        image = request.form['image']
        # update book data
        book.name = name
        book.price = price
        book.description = description
        book.category = category
        book.image = image
        # commit changes to database
        db.session.commit()
        # return to same page
        return redirect(url_for('views.newBooks'))
    return render_template("update_book.html", book=book)


# route to add book to cart
@views.route('/addtocart')
def addtocart():
    # get book id from request args
    book_id = request.args.get('book_id')

    # check if book is already in cart
    # get all items in cart
    items = Cart.query.all()
    # get book_id of each item
    book_ids = [item.book_id for item in items]
    # if book_id is in book_ids, then book is already in cart
    if not int(book_id) in book_ids:
        # add book_id to cart if it is not already in cart
        new_item = Cart(book_id=book_id)
        # add new item to Cart table in database
        db.session.add(new_item)

    # if book is already in cart, increase quantity by 1
    # increase book quantity by 1
    book = Book.query.filter_by(id=book_id).first()
    book.quantity += 1

    # commit changes to database
    db.session.commit()

    # flash message (to let user know book has been added to cart)
    flash('Book added to cart!')
    # return to same page
    return redirect(url_for('views.newBooks'))


# route to manage cart
@views.route("/shoppingCart")
def shoppingCart():
    # get all items in cart
    items = Cart.query.all()
    # get book_id of each item
    book_ids = [item.book_id for item in items]
    # get book object for each book_id
    books = [Book.query.filter_by(id=book_id).first() for book_id in book_ids]
    # determine total price of all items in cart taking into account quantity
    total_book_price = [float(book.price) * book.quantity for book in books]
    total_price = round(sum(total_book_price), 2)

    # check if book quantity is 0 and delete from cart if it is
    for book in books:
        if book.quantity == 0:
            # get cart item
            cart_item = Cart.query.filter_by(book_id=book.id).first()
            # delete cart item
            db.session.delete(cart_item)
            db.session.commit()
            # return to shopping cart page
            return redirect(url_for('views.shoppingCart'))

    # return shoppingCart.html page and pass in books and total price
    return render_template("shoppingCart.html", books=books, total_price=total_price)


# delete all books route (for testing purposes)
# going to this route will delete all books from database so only use for testing purposes when needed
@views.route('/delete_all_books')
def deleteallbooks():
    # get all books
    books = Book.query.all()
    # delete each book from Book table in database
    for book in books:
        db.session.delete(book)
        db.session.commit()
    # return to same page
    return redirect(url_for('views.newBooks'))


# increase book quantity route (in cart)
@views.route('/increase_quantity')
def increasequantity():
    # get id from request args (passed in from a tag (button) in shoppingCart.html)
    book_id = request.args.get('book_id')
    # get book object
    book = Book.query.filter_by(id=book_id).first()
    # increase quantity by 1
    book.quantity += 1
    # commit changes to database
    db.session.commit()
    # return to cart page
    return redirect(url_for('views.shoppingCart'))


# decrease book quantity route (in cart)
@views.route('/decrease_quantity')
def decreasequantity():
    # get id from request args
    book_id = request.args.get('book_id')
    # get book object
    book = Book.query.filter_by(id=book_id).first()
    # decrease quantity by 1
    book.quantity -= 1
    # if quantity is 0, remove book from cart
    if book.quantity == 0:
        # get cart item with book_id
        item = Cart.query.filter_by(book_id=book_id).first()
        # delete cart item
        db.session.delete(item)
    # commit changes to database
    db.session.commit()
    return redirect(url_for('views.shoppingCart'))


# remove book from cart
@views.route('/remove_from_cart')
def removefromcart():
    # get book id from request args
    book_id = request.args.get('book_id')
    # get cart item with book_id
    item = Cart.query.filter_by(book_id=book_id).first()
    # make book quantity 0
    book = Book.query.filter_by(id=book_id).first()
    book.quantity = 0
    # delete cart item
    db.session.delete(item)
    db.session.commit()
    print(f'book with ID: {book_id} removed from cart!')
    # return to same page
    return redirect(url_for('views.shoppingCart'))


# confirm order route
@views.route('/confirm_order', methods=['GET', 'POST'])
def confirm_order():
    # check if cart is empty
    if Cart.query.all() == []:
        # redirect to new books page if cart is empty as makes no sense to confirm order if cart is empty
        return redirect(url_for('views.newBooks'))

    # check if user is logged in
    if current_user.is_authenticated:
        # create order form
        form = OrderForm()
        # get current user
        user = User.query.filter_by(id=current_user.id).first()

        # get all items in cart
        items = Cart.query.all()
        # get book_id of each item
        book_ids = [item.book_id for item in items]
        # get book object for each book_id
        books = [Book.query.filter_by(id=book_id).first()
                 for book_id in book_ids]
        # determine total price of all items in cart taking into account quantity
        total_book_price = [
            float(book.price) * book.quantity for book in books]
        total_price = round(sum(total_book_price), 2)

        # handle POST request
        if request.method == 'POST':
            # get order data from form
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            phone = form.phone.data
            address = form.address.data

            # create new order object
            new_order = Order(first_name=first_name, last_name=last_name, email=email,
                              phone=phone, address=address, total_cost=total_price)
            # add order to database
            db.session.add(new_order)
            db.session.commit()

            # set quantity of each book to 0
            for book in books:
                book.quantity = 0
                db.session.commit()

            # delete all items from cart (clear cart after order)
            for item in items:
                db.session.delete(item)
                db.session.commit()

            # return to success page and display order details by passing in order, price, books and user
            return render_template('success.html', order=new_order, books=books, user=user, total_cost=total_price)
        # display order form and prepopulate some fields by passing in user, total price and books
        return render_template('order.html', form=form, user=user, total_cost=total_price, books=books)
    else:
        # redirect to login page
        return redirect(url_for('auth.login'))


# fiction books route
@views.route("/fictionBooks")
def fictionBooks():
    # get all books where category is fiction
    books = Book.query.filter_by(category='fiction').all()
    # return fictionBooks.html page and pass in books
    return render_template("fictionBooks.html", books=books)


# non-fiction books route
@views.route("/nonFictionBooks")
def nonfictionBooks():
    # get all books where category is nonfiction
    books = Book.query.filter_by(category='non-fiction').all()
    # return nonfictionBooks.html page and pass in books
    return render_template("nonfictionBooks.html", books=books)


# book details route
@views.route("/bookDetails")
def bookDetails():
    # get book id from request
    book_id = request.args.get('book_id')
    # get book object
    book = Book.query.filter_by(id=book_id).first()
    # return bookDetails.html page and pass in book to display book details
    return render_template("book_details.html", book=book)
