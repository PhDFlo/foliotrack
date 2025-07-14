from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF
import numpy as np
import matplotlib.pyplot as plt

def main():
    
    # Create an ETF instance
    etf1 = ETF(name="Amundi MSCI World UCITS ETF", ticker="AMDW", currency="Euro", price=500.0, fees=0.2)
    etf2 = ETF(name="Vanguard S&P 500 UCITS ETF", ticker="VUSA", currency="USD", price=300.0, fees=0.1)
    etf3 = ETF(name="iShares Core MSCI Emerging Markets IMI UCITS ETF", ticker="EIMI", currency="Euro", price=200.0, fees=0.25)
    
    # Create a PortfolioETF instance
    portfolio = PortfolioETF()
    portfolio.add_etf(etf1, portfolio_share=0.5, amount_invested=2000.0)
    portfolio.add_etf(etf2, portfolio_share=0.2, amount_invested=800.0)
    portfolio.add_etf(etf3, portfolio_share=0.3, amount_invested=300.0)
    
    # Solve for equilibrium
    #equilibrium = portfolio.solve_equilibrium(etf3, 0.)
    equilibrium = portfolio.solve_equilibrium(etf1, 20.)
    
    for elem in equilibrium:
        print(f"ETF: {elem['etf'].name}")
        print(f"   Target share: {elem['portfolio_share']},  Actual share: {elem['actual_share']}, Final Share: {elem['final_share']}")
        print(f"   Amount Invested: {elem['amount_invested']}€, Amount to Invest: {elem['amount_to_invest']}€")

    print(f"Total to invest: {portfolio.total_to_invest}€")
    
    # # Loop over the invested moment
    # Select_ETF = etf1
    # Tot_invest_list = []
    # Invest_val = np.linspace(0., 1000., 100)
    
    # for val in Invest_val:
    #     equilibrium = portfolio.solve_equilibrium(Select_ETF, val)
    #     print("")
    #     Tot_invest_list.append(portfolio.total_to_invest)
        
    # # Plot evolution
    # plt.figure()
    # plt.plot(Invest_val, Tot_invest_list)
    # plt.savefig("test.png")
        

if __name__ == "__main__":
    main()