CREATE TABLE "User"(
    id VARCHAR(256) PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    permission INTEGER NOT NULL DEFAULT (1),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    location VARCHAR(50) NOT NULL,
    password VARCHAR(256) NOT NULL,
    agreement BOOLEAN,
    blocked BOOLEAN DEFAULT FALSE,
    id_file BYTEA NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE "Category"(
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE "Item"(
    id VARCHAR(256) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT ('כללי'),
    amount INTEGER CHECK ( amount >= 0 ) NOT NULL,
    total_amount INTEGER CHECK ( total_amount >= 0 ) NOT NULL,
    price FLOAT CHECK ( price > 0 ) NOT NULL,
    notes VARCHAR(100),
    description VARCHAR(256),
    condition VARCHAR(100),
    hidden BOOLEAN NOT NULL DEFAULT FALSE,
    image VARCHAR(64),
    FOREIGN KEY (category) REFERENCES "Category"(name) ON DELETE SET DEFAULT
);

CREATE TABLE "Cart"(
    id VARCHAR(256) PRIMARY KEY,
    user_id VARCHAR(256) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT ('ACTIVE'),
    FOREIGN KEY (user_id) REFERENCES "User"(id) ON DELETE CASCADE
);

CREATE TABLE "CartItem"(
    cart_id VARCHAR(256) NOT NULL,
    item_id VARCHAR(256) NOT NULL,
    amount INTEGER NOT NULL DEFAULT (1),
    FOREIGN KEY (cart_id) REFERENCES "Cart"(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES "Item"(id) ON DELETE CASCADE,
    PRIMARY KEY (cart_id, item_id)
);

CREATE TABLE "Order"(
    cart_id VARCHAR(256) PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    submission_date DATE NOT NULL,
    finalization_date DATE,
    total_price INTEGER NOT NULL CHECK ( total_price > 0 ),
    status VARCHAR(20) NOT NULL,
    customer_notes VARCHAR(500),
    FOREIGN KEY (cart_id) REFERENCES "Cart"(id) ON DELETE CASCADE
);
