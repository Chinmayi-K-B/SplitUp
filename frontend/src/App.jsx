import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
const GROUP_ID = 1;

// Temporary demo user.
// Proper authentication can be added later.
const CURRENT_USER_ID = 1;

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [users, setUsers] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [balances, setBalances] = useState({});
  const [settlement, setSettlement] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Add Expense form state
  const [showExpenseForm, setShowExpenseForm] = useState(false);

  const [formData, setFormData] = useState({
    description: "",
    amount: "",
    paid_by: CURRENT_USER_ID,
    split_user_ids: [CURRENT_USER_ID],
  });

  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const navigation = [
    { id: "dashboard", label: "Dashboard", icon: "⌂" },
    { id: "expenses", label: "Expenses", icon: "₹" },
    { id: "recurring", label: "Recurring", icon: "↻" },
    { id: "settlement", label: "Settlement", icon: "⇄" },
  ];

  // ---------------------------------------------------------
  // Load backend data when the application starts
  // ---------------------------------------------------------

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError("");

      const [
        usersResponse,
        expensesResponse,
        balancesResponse,
        settlementResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/users`),
        fetch(`${API_URL}/expenses`),
        fetch(`${API_URL}/groups/${GROUP_ID}/balances`),
        fetch(`${API_URL}/groups/${GROUP_ID}/settlement`),
      ]);

      if (
        !usersResponse.ok ||
        !expensesResponse.ok ||
        !balancesResponse.ok ||
        !settlementResponse.ok
      ) {
        throw new Error("Failed to load data from the backend.");
      }

      const usersData = await usersResponse.json();
      const expensesData = await expensesResponse.json();
      const balancesData = await balancesResponse.json();
      const settlementData = await settlementResponse.json();

      setUsers(usersData);
      setExpenses(expensesData);
      setBalances(balancesData.balances);
      setSettlement(settlementData.settlement);
    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to the SplitUp backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------
  // Refresh data after adding an expense
  // ---------------------------------------------------------

  async function reloadData() {
    try {
      setError("");

      const [
        usersResponse,
        expensesResponse,
        balancesResponse,
        settlementResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/users`),
        fetch(`${API_URL}/expenses`),
        fetch(`${API_URL}/groups/${GROUP_ID}/balances`),
        fetch(`${API_URL}/groups/${GROUP_ID}/settlement`),
      ]);

      if (
        !usersResponse.ok ||
        !expensesResponse.ok ||
        !balancesResponse.ok ||
        !settlementResponse.ok
      ) {
        throw new Error("Failed to refresh data.");
      }

      const usersData = await usersResponse.json();
      const expensesData = await expensesResponse.json();
      const balancesData = await balancesResponse.json();
      const settlementData = await settlementResponse.json();

      setUsers(usersData);
      setExpenses(expensesData);
      setBalances(balancesData.balances);
      setSettlement(settlementData.settlement);
    } catch (err) {
      console.error(err);
      setError("Failed to refresh SplitUp data.");
    }
  }

  // ---------------------------------------------------------
  // Add Expense
  // ---------------------------------------------------------

  async function handleAddExpense(event) {
    event.preventDefault();

    setFormError("");

    if (!formData.description.trim()) {
      setFormError("Please enter an expense description.");
      return;
    }

    if (!formData.amount || Number(formData.amount) <= 0) {
      setFormError("Please enter a valid amount.");
      return;
    }

    if (formData.split_user_ids.length === 0) {
      setFormError(
        "Select at least one person to split the expense."
      );
      return;
    }

    try {
      setSubmitting(true);

      // Generate the next expense ID.
      const nextId =
        expenses.length > 0
          ? Math.max(...expenses.map((expense) => expense.id)) + 1
          : 1;

      const response = await fetch(`${API_URL}/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: nextId,
          group_id: GROUP_ID,
          description: formData.description.trim(),
          amount: Number(formData.amount),
          paid_by: Number(formData.paid_by),
          created_at: new Date().toISOString(),
          is_recurring: false,
          split_user_ids: formData.split_user_ids,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to add expense."
        );
      }

      // Clear the form.
      setFormData({
        description: "",
        amount: "",
        paid_by: CURRENT_USER_ID,
        split_user_ids: [CURRENT_USER_ID],
      });

      // Close modal.
      setShowExpenseForm(false);

      // Reload actual database data.
      await reloadData();
    } catch (err) {
      console.error(err);
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  // ---------------------------------------------------------
  // Helper functions
  // ---------------------------------------------------------

  const currentUser = users.find(
    (user) => user.id === CURRENT_USER_ID
  );

  const currentBalance = Number(
    balances[String(CURRENT_USER_ID)] || 0
  );

  const totalSpending = expenses.reduce(
    (total, expense) => total + Number(expense.amount),
    0
  );

  const getUserName = (userId) => {
    const user = users.find(
      (user) => user.id === userId
    );

    return user ? user.name : `User ${userId}`;
  };

  // ---------------------------------------------------------
  // Main UI
  // ---------------------------------------------------------

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div>
            <h1>SplitUp</h1>
            <p>Shared expenses, simplified.</p>
          </div>
        </div>

        <nav>
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="group-mini">
            <div className="group-avatar">R</div>

            <div>
              <strong>Roommates</strong>
              <span>{users.length} members</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main area */}
      <main className="main">
        {/* Top bar */}
        <header className="topbar">
          <div>
            <p className="eyebrow">GROUP</p>
            <h2>Roommates</h2>
          </div>

          <div className="profile">
            <div className="profile-avatar">
              {currentUser?.name?.[0] || "U"}
            </div>

            <div>
              <strong>
                {currentUser?.name || "User"}
              </strong>

              <span>Member</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <section className="content">
          {loading && (
            <div className="placeholder">
              <p className="eyebrow">SPLITUP</p>
              <h3>Loading your expenses...</h3>
            </div>
          )}

          {!loading && error && (
            <div className="placeholder">
              <p className="eyebrow">
                CONNECTION ERROR
              </p>

              <h3>Backend unavailable</h3>

              <p>{error}</p>
            </div>
          )}

          {!loading &&
            !error &&
            activePage === "dashboard" && (
              <Dashboard
                currentUser={currentUser}
                currentBalance={currentBalance}
                totalSpending={totalSpending}
                expenses={expenses}
                settlement={settlement}
                getUserName={getUserName}
                onAddExpense={() => {
                  setFormError("");
                  setShowExpenseForm(true);
                }}
              />
            )}

          {!loading &&
            !error &&
            activePage === "expenses" && (
              <ExpensesPage
                expenses={expenses}
                getUserName={getUserName}
                onAddExpense={() => {
                  setFormError("");
                  setShowExpenseForm(true);
                }}
              />
            )}

          {!loading &&
            !error &&
            activePage === "recurring" && (
              <Placeholder
                title="Recurring Expenses"
                description="Recurring expense management will be connected next."
              />
            )}

          {!loading &&
            !error &&
            activePage === "settlement" && (
              <SettlementPage
                settlement={settlement}
                getUserName={getUserName}
              />
            )}
        </section>
      </main>

      {/* Add Expense Modal */}
      {showExpenseForm && (
        <div className="modal-overlay">
          <div className="expense-modal">
            <div className="modal-header">
              <div>
                <p className="eyebrow">NEW EXPENSE</p>
                <h3>Add an expense</h3>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setShowExpenseForm(false)
                }
              >
                ×
              </button>
            </div>

            <form onSubmit={handleAddExpense}>
              {/* Description */}
              <label>
                Description

                <input
                  type="text"
                  placeholder="e.g. Groceries"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      description: e.target.value,
                    })
                  }
                />
              </label>

              {/* Amount */}
              <label>
                Amount

                <input
                  type="number"
                  min="1"
                  step="0.01"
                  placeholder="₹ 0"
                  value={formData.amount}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      amount: e.target.value,
                    })
                  }
                />
              </label>

              {/* Paid by */}
              <label>
                Paid by

                <select
                  value={formData.paid_by}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      paid_by: Number(e.target.value),
                    })
                  }
                >
                  {users.map((user) => (
                    <option
                      key={user.id}
                      value={user.id}
                    >
                      {user.name}
                    </option>
                  ))}
                </select>
              </label>

              {/* Split users */}
              <div className="split-section">
                <p className="form-label">
                  Split between
                </p>

                {users.map((user) => (
                  <label
                    className="checkbox-row"
                    key={user.id}
                  >
                    <input
                      type="checkbox"
                      checked={formData.split_user_ids.includes(
                        user.id
                      )}
                      onChange={() => {
                        const selected =
                          formData.split_user_ids;

                        setFormData({
                          ...formData,
                          split_user_ids:
                            selected.includes(user.id)
                              ? selected.filter(
                                  (id) =>
                                    id !== user.id
                                )
                              : [
                                  ...selected,
                                  user.id,
                                ],
                        });
                      }}
                    />

                    <span>{user.name}</span>
                  </label>
                ))}
              </div>

              {/* Error */}
              {formError && (
                <p className="form-error">
                  {formError}
                </p>
              )}

              {/* Submit */}
              <button
                type="submit"
                className="primary-button submit-button"
                disabled={submitting}
              >
                {submitting
                  ? "Adding..."
                  : "Add Expense"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}


// =========================================================
// Dashboard
// =========================================================

function Dashboard({
  currentUser,
  currentBalance,
  totalSpending,
  expenses,
  settlement,
  getUserName,
  onAddExpense,
}) {
  const recentExpenses = expenses.slice(0, 5);

  const amountYouOwe =
    currentBalance < 0
      ? Math.abs(currentBalance)
      : 0;

  const amountOwedToYou =
    currentBalance > 0
      ? currentBalance
      : 0;

  return (
    <>
      <div className="welcome">
        <div>
          <p className="eyebrow">OVERVIEW</p>

          <h3>
            Good to see you back
            {currentUser
              ? `, ${currentUser.name}`
              : ""}{" "}
            👋
          </h3>

          <p>
            Here's what's happening with your shared
            expenses.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={onAddExpense}
        >
          + Add Expense
        </button>
      </div>

      <div className="stats-grid">
        <StatCard
          label="You owe"
          amount={`₹${amountYouOwe.toLocaleString(
            "en-IN"
          )}`}
          detail={
            amountYouOwe > 0
              ? "to your roommates"
              : "nothing pending"
          }
          type="owe"
        />

        <StatCard
          label="You're owed"
          amount={`₹${amountOwedToYou.toLocaleString(
            "en-IN"
          )}`}
          detail={
            amountOwedToYou > 0
              ? "from your roommates"
              : "nothing pending"
          }
          type="receive"
        />

        <StatCard
          label="Group spending"
          amount={`₹${totalSpending.toLocaleString(
            "en-IN"
          )}`}
          detail="recorded expenses"
          type="total"
        />
      </div>

      <div className="dashboard-grid">
        {/* Recent expenses */}
        <section className="card">
          <div className="card-header">
            <div>
              <p className="eyebrow">RECENT</p>
              <h4>Recent expenses</h4>
            </div>

            <span className="status-badge">
              {expenses.length} total
            </span>
          </div>

          {recentExpenses.length === 0 ? (
            <p className="empty-message">
              No expenses recorded yet.
            </p>
          ) : (
            recentExpenses.map((expense) => (
              <ExpenseRow
                key={expense.id}
                title={expense.description}
                date={formatDate(
                  expense.created_at
                )}
                amount={`₹${Number(
                  expense.amount
                ).toLocaleString("en-IN")}`}
                payer={getUserName(
                  expense.paid_by
                )}
              />
            ))
          )}
        </section>

        {/* Settlement */}
        <section className="card">
          <div className="card-header">
            <div>
              <p className="eyebrow">
                SETTLEMENT
              </p>

              <h4>Settlement plan</h4>
            </div>

            <span className="status-badge">
              {settlement.length} payments
            </span>
          </div>

          {settlement.length === 0 ? (
            <p className="empty-message">
              Everyone is settled.
            </p>
          ) : (
            settlement
              .slice(0, 4)
              .map((transaction, index) => (
                <SettlementRow
                  key={index}
                  payer={getUserName(
                    transaction[0]
                  )}
                  receiver={getUserName(
                    transaction[1]
                  )}
                  amount={transaction[2]}
                />
              ))
          )}

          {settlement.length > 0 && (
            <button className="secondary-button">
              View settlement plan
            </button>
          )}
        </section>
      </div>
    </>
  );
}


// =========================================================
// Expenses Page
// =========================================================

function ExpensesPage({
  expenses,
  getUserName,
  onAddExpense,
}) {
  return (
    <div>
      <div className="welcome">
        <div>
          <p className="eyebrow">EXPENSES</p>

          <h3>All expenses</h3>

          <p>
            Every shared expense recorded for the
            group.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={onAddExpense}
        >
          + Add Expense
        </button>
      </div>

      <section className="card">
        {expenses.length === 0 ? (
          <p className="empty-message">
            No expenses recorded yet.
          </p>
        ) : (
          expenses.map((expense) => (
            <ExpenseRow
              key={expense.id}
              title={expense.description}
              date={formatDate(
                expense.created_at
              )}
              amount={`₹${Number(
                expense.amount
              ).toLocaleString("en-IN")}`}
              payer={getUserName(
                expense.paid_by
              )}
            />
          ))
        )}
      </section>
    </div>
  );
}


// =========================================================
// Settlement Page
// =========================================================

function SettlementPage({
  settlement,
  getUserName,
}) {
  return (
    <div>
      <div className="welcome">
        <div>
          <p className="eyebrow">
            SETTLEMENT
          </p>

          <h3>Settle up</h3>

          <p>
            A practical plan for settling the group's
            balances.
          </p>
        </div>
      </div>

      <section className="card">
        {settlement.length === 0 ? (
          <div className="empty-message">
            Everyone is settled. 🎉
          </div>
        ) : (
          settlement.map((transaction, index) => (
            <SettlementRow
              key={index}
              payer={getUserName(
                transaction[0]
              )}
              receiver={getUserName(
                transaction[1]
              )}
              amount={transaction[2]}
            />
          ))
        )}
      </section>
    </div>
  );
}


// =========================================================
// Reusable Components
// =========================================================

function StatCard({
  label,
  amount,
  detail,
  type,
}) {
  return (
    <div className={`stat-card ${type}`}>
      <div className="stat-icon">
        {type === "owe"
          ? "↓"
          : type === "receive"
          ? "↑"
          : "₹"}
      </div>

      <p>{label}</p>

      <h3>{amount}</h3>

      <span>{detail}</span>
    </div>
  );
}


function ExpenseRow({
  title,
  date,
  amount,
  payer,
}) {
  return (
    <div className="expense-row">
      <div className="expense-icon">₹</div>

      <div className="expense-info">
        <strong>{title}</strong>

        <span>
          {date} · Paid by {payer}
        </span>
      </div>

      <strong>{amount}</strong>
    </div>
  );
}


function SettlementRow({
  payer,
  receiver,
  amount,
}) {
  return (
    <div className="settlement-row">
      <div className="member-avatar">
        {payer[0]}
      </div>

      <div>
        <strong>
          {payer} → {receiver}
        </strong>

        <span>Settlement payment</span>
      </div>

      <strong>
        ₹{Number(amount).toLocaleString("en-IN")}
      </strong>
    </div>
  );
}


function Placeholder({
  title,
  description,
}) {
  return (
    <div className="placeholder">
      <p className="eyebrow">SPLITUP</p>

      <h3>{title}</h3>

      <p>
        {description ||
          "This section will be connected to the FastAPI backend next."}
      </p>
    </div>
  );
}


// =========================================================
// Date formatting
// =========================================================

function formatDate(dateString) {
  if (!dateString) {
    return "Unknown date";
  }

  return new Date(dateString).toLocaleDateString(
    "en-IN",
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    }
  );
}


export default App;