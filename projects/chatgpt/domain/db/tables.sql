CREATE TABLE  if not exists Account (
    id VARCHAR(255) PRIMARY KEY,
    account_type VARCHAR(255),
    account_name VARCHAR(255)
);

COMMENT ON TABLE Account IS 'Table for storing account details';
COMMENT ON COLUMN Account.id IS 'Unique identifier for each account';
COMMENT ON COLUMN Account.account_type IS 'Type of the account e.g. savings, checking, credit card, investment, mortgage, personal loan, etc';
COMMENT ON COLUMN Account.account_name IS 'Name of the account e.g. Primary Checking, Student Loan, Chase Saphire Credit Card';

CREATE TABLE if not exists Transaction (
    id VARCHAR(255) PRIMARY KEY,
    date DATE,
    amount FLOAT,
    description TEXT,
    type varchar(255),
    category VARCHAR(255),
    account_id VARCHAR(255) REFERENCES Account(id)
);

COMMENT ON TABLE Transaction IS 'Table for storing transaction details for accounts';
COMMENT ON COLUMN Transaction.id IS 'Unique identifier for each transaction';
COMMENT ON COLUMN Transaction.date IS 'Date when the transaction occurred. e.g. "12/5/22"';
COMMENT ON COLUMN Transaction.amount IS 'Amount of money involved in the transaction';
COMMENT ON COLUMN Transaction.description IS 'Description of the transaction which includes the other parties involved in the transaction.  e.g. "DELTA AIR   0062355335690", "TRADER JOE''S #350 QPS", "UBER   TRIP" ';
COMMENT ON COLUMN Transaction.type IS 'The credit or debit type. e.g. "Sale", "Payment"';
COMMENT ON COLUMN Transaction.category IS 'Category of the transaction (e.g., groceries, utilities, Loan payment, ACH Credit, Other, Food & Drink, Gifts & Donations)';
COMMENT ON COLUMN Transaction.account_id IS 'Reference to the account this transaction belongs to, links to the Account table';