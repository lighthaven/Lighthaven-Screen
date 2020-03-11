import pandas as pd


def execute(ticker):
    # Helpers to remove %, B, M from tables and convert to float
    def remove_percent(input):
        new_input = input
        if (type(input) == str):
            x = input.find('%')
            if (x != -1):
                new_input = new_input[0:x]
        return new_input


    def remove_tril(input):
        new_input = input
        if (type(input) == str):
            new_input = input
            x = input.find('T')
            if (x != -1):
                new_input = new_input[0:x]
        return new_input

    def remove_bil(input):
        new_input = input
        if (type(input) == str):
            new_input = input
            x = input.find('B')
            if (x != -1):
                new_input = new_input[0:x]
                new_input = float(new_input) * 1000
        return new_input

    def remove_mil(input):
        new_input = input
        if (type(input) == str):
            new_input = input
            x = input.find('M')
            if (x != -1):
                new_input = new_input[0:x]
        return new_input

    def remove_dash(input):
        new_input = input
        if (type(input) == str):
            if (input == '-'):
                new_input = '0'
        return new_input

    def remove_comma(input):
        new_input = input
        x = input.find(',')
        if (x != -1):
            new_input = new_input.replace(',', '')
        return new_input

    def fix_negative(input):
        new_input = input
        x = input.find('(')
        if (x != -1):
            new_input = new_input.replace('(', '-')
        y = input.find(')')
        if (y != -1):
            new_input = new_input.replace(')', '')
        return new_input

    def clean_string(input):
        input = remove_dash(input)
        input = remove_comma(input)
        input = fix_negative(input)
        input = remove_percent(input)
        input = remove_bil(input)
        input = remove_tril(input)
        input = remove_mil(input)
        input = round(float(input), 3)
        return (input)

    def clean_table(df):
        for col in range(df.shape[1]):
            for row in range(df.shape[0]):
                df.iloc[row][col] = clean_string(df.iloc[row][col])
                df.iloc[row][col] = float(df.iloc[row][col])
        return df

    def remove_bil_fundamental(input):
        new_input = input

        if (type(input) == str):

            z = input.find('T')
            if (z != -1):
                new_input = new_input[0:z]
                new_input = float(new_input) * 1000 * 1000

            x = input.find('B')
            if (x != -1):
                new_input = new_input[0:x]
                new_input = float(new_input) * 1000

            y = input.find('M')
            if (y != -1):
                new_input = float(new_input[0:y])
        return new_input

    # Annual Financials

    try:
        annual_rev_df = pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker + '/financials')[0]
        annual_NI_df = pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker + '/financials')[1]
        annual_cash_df = \
            pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/balance-sheet')[0]
        annual_debt_df = \
            pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/balance-sheet')[2]
        annual_fcf_df = pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/cash-flow')[
            2]
    except:
        return("Could not scrape yearly financial data")

    annual_rev_df.columns.values[0] = "METRIC"
    annual_NI_df.columns.values[0] = "METRIC"
    annual_cash_df.columns.values[0] = "METRIC"
    annual_debt_df.columns.values[0] = "METRIC"
    annual_fcf_df.columns.values[0] = "METRIC"

    annual_rev_df = annual_rev_df.loc[[0, 1], :]  # Sales and Sales Growth
    annual_EPS_df = annual_NI_df.loc[annual_NI_df.METRIC == 'EPS (Diluted)']
    annual_EPS_growth_df = annual_NI_df.loc[annual_NI_df.METRIC == 'EPS (Diluted) Growth']
    annual_NI_df = annual_EPS_df.append(annual_EPS_growth_df)  # EPS and EPS Growth
    annual_cash_df = annual_cash_df.loc[[0]]  # Cash and ST Securities
    annual_debt_df = annual_debt_df.loc[annual_debt_df.METRIC == 'Long-Term Debt']  # Debt
    annual_fcf_df = annual_fcf_df.loc[annual_fcf_df.METRIC == 'Free Cash Flow']  # FCF


    annual_financials_df = annual_rev_df.append(
        annual_NI_df.append(annual_debt_df.append(annual_cash_df.append(annual_fcf_df))))
    annual_financials_df = annual_financials_df.drop(columns='5-year trend')
    annual_financials_df = annual_financials_df.set_index(['METRIC'])
    annual_financials_df = annual_financials_df.rename({'Sales Growth': 'Sales Growth (%)',
                                                        'EPS (Diluted) Growth': 'EPS Growth (%)'})
    annual_financials_df = clean_table(annual_financials_df)

    # Quarterly Financials
    try:
        quarterly_financial_rev_df = pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker +
                                                  '/financials/income/quarter')[0]
        quarterly_financial_NI_df = pd.read_html('https://www.marketwatch.com/investing/stock/' + ticker +
                                                 '/financials/income/quarter')[1]
    except:
        return ("Could not scrape quarterly financial data")

    quarterly_financial_rev_df.columns.values[0] = 'METRIC'
    quarterly_financial_NI_df.columns.values[0] = 'METRIC'

    quarterly_financial_rev_df = quarterly_financial_rev_df.loc[[0, 1], :]  # Sales and Sales Growth
    quarterly_EPS_df = quarterly_financial_NI_df.loc[quarterly_financial_NI_df.METRIC == 'EPS (Diluted)']
    quarterly_EPS_growth_df = quarterly_financial_NI_df.loc[quarterly_financial_NI_df.METRIC == 'EPS (Diluted) Growth']
    quarterly_financial_NI_df = quarterly_EPS_df.append(quarterly_EPS_growth_df)  # EPS and EPS Growth

    quarterly_financials_df = quarterly_financial_rev_df.append(quarterly_financial_NI_df)
    quarterly_financials_df = quarterly_financials_df.drop(columns='5-qtr trend')
    quarterly_financials_df = quarterly_financials_df.set_index(['METRIC'])
    quarterly_financials_df = quarterly_financials_df.rename({'Sales Growth': 'Sales Growth (%)',
                                                              'EPS (Diluted) Growth': 'EPS Growth (%)'})
    quarterly_financials_df = clean_table(quarterly_financials_df)

    # Fundamental Data
    url = 'https://finance.yahoo.com/quote/' + ticker + '?p=' + ticker

    fund_1_df = pd.read_html(url)[0]
    fund_2_df = pd.read_html(url)[1]

    fundamental_df = pd.concat([fund_1_df, fund_2_df])

    fundamental_df = fundamental_df.reset_index(drop=True)
    fundamental_df = fundamental_df.iloc[[0, 5, 8, 10], :]
    fundamental_df.columns = ['METRIC', 'VALUE']
    fundamental_df = fundamental_df.set_index(['METRIC'])
    fundamental_df.iloc[0][0] = float(fundamental_df.iloc[0][0])
    fundamental_df.iloc[2][0] = remove_bil_fundamental(fundamental_df.iloc[2][0])
    fundamental_df.iloc[3][0] = float(fundamental_df.iloc[3][0])
    fundamental_df = fundamental_df.rename({'Market Cap': 'Market Cap (Mil)'})

    # Long Screen Tables
    # Fast Grower
    fast_data = [['Revenue Growth >15% last 3 yrs', False], ['EPS Growth >15% last 3 yrs', False],
                 ['LTD/Cash + Securities <= 2', False], ['Positive FCF last 3 years', False], ['Distrupting the status quo', 'Subjective']]
    fast_grower = pd.DataFrame(fast_data, columns=['FAST GROWER (LONG)', 'STATUS'])
    fast_grower = fast_grower.set_index(['FAST GROWER (LONG)'])

    # Stalwart
    stalwart_data = [['Revenue Growth >10% last 3 yrs', False], ['EPS Growth >10% last 3 yrs', False],
                     ['Market Cap >$100MM', False], ['Mature company but still growing', 'Subjective']]
    stalwart = pd.DataFrame(stalwart_data, columns=['STALWART (LONG)', 'STATUS'])
    stalwart = stalwart.set_index(['STALWART (LONG)'])

    # Surfer
    surfer_data = [['Revenue Growth >35% last 3 yrs', False],
                   ['Company will dominate industry', 'Subjective'],
                   ['Company will create industry', 'Subjective'],
                   ['Company will disrupt industry', 'Subjective']]
    surfer = pd.DataFrame(surfer_data, columns=['SURFER (LONG)', 'STATUS'])
    surfer = surfer.set_index(['SURFER (LONG)'])

    # Short Screen Tables
    # Dead Company
    dead_data = [['Declining EPS last 4 qts', False], ['Declinging Revenue last 4 qts', False],
                 ['LTD/Cash + Securities >= 2', False], ['Negative FCF', False], ['Company is being disrupted', 'Subjective']]
    dead_walking = pd.DataFrame(dead_data, columns=['DEAD COMPANY (SHORT)', 'STATUS'])
    dead_walking = dead_walking.set_index(['DEAD COMPANY (SHORT)'])

    # Fad
    fad_data = [['Revenue Growth >40% last 3 yrs', False], ['Positve Earnings TTM', False],
                ['EPS declined most recent qtr', False], ['Product/service is a fad', 'Subjective']]
    fad = pd.DataFrame(fad_data, columns=['FAD STOCK (SHORT)', 'STATUS'])
    fad = fad.set_index(['FAD STOCK (SHORT)'])

    # Hot Story
    hot_data = [['Price increased dramatically, levelling off', 'Subjective'],
                ['Many competitors', 'Subjective'], ['High PE ratio', False], ['Industry the public is excited about', 'Subjective']]
    hot_story = pd.DataFrame(hot_data, columns=['HOT STORY (SHORT)', 'STATUS'])
    hot_story = hot_story.set_index(['HOT STORY (SHORT)'])

    # Fast_Grower Screen
    def fast_rev(df):
        if (df.iloc[1, -1] >= 14.5 and df.iloc[1, -2] >= 14.5 and df.iloc[1, -3] >= 14.5):
            return 'True'
        else:
            return 'False'

    def fast_eps(df):
        if (df.iloc[3, -1] >= 14.5 and df.iloc[3, -2] >= 14.5 and df.iloc[3, -3] >= 14.5):
            return 'True'
        else:
            return 'False'

    def fast_debt_cash(df):
        cash_securities = df.iloc[5, -1]
        debt = df.iloc[4, -1]
        if (debt / cash_securities <= 2):
            return 'True'
        else:
            return 'False'

    def fast_fcf(df):
        if (df.iloc[6, -1] > 0 and df.iloc[6, -2] > 0 and df.iloc[6, -3] > 0):
            return 'True'
        else:
            return 'False'

    def update_fast_grower(df):
        df.iloc[0, 0] = fast_rev(annual_financials_df)
        df.iloc[1, 0] = fast_eps(annual_financials_df)
        df.iloc[2, 0] = fast_debt_cash(annual_financials_df)
        df.iloc[3, 0] = fast_fcf(annual_financials_df)
        return df

    # Stalwart Screen
    def stalwart_rev(df):
        if (df.iloc[1, -1] >= 9.5 and df.iloc[1, -2] >= 9.5 and df.iloc[1, -3] >= 9.5):
            return 'True'
        else:
            return 'False'

    def stalwart_eps(df):
        if (df.iloc[3, -1] >= 9.5 and df.iloc[3, -2] >= 9.5 and df.iloc[3, -3] >= 9.5):
            return 'True'
        else:
            return 'False'

    def stalwart_market_cap(df):
        if (df.iloc[2, 0] >= 100):
            return 'True'
        else:
            return 'False'

    def update_stalwart(df):
        df.iloc[0, 0] = stalwart_rev(annual_financials_df)
        df.iloc[1, 0] = stalwart_eps(annual_financials_df)
        df.iloc[2, 0] = stalwart_market_cap(fundamental_df)
        return df

    # Surfer Screen
    def surfer_rev(df):
        if (df.iloc[1, -1] >= 34.5 and df.iloc[1, -2] >= 34.5 and df.iloc[1, -3] >= 34.5):
            return 'True'
        else:
            return 'False'

    def update_surfer(df):
        df.iloc[0, 0] = surfer_rev(annual_financials_df)
        return df

    # Dead Walking Screen
    def dead_eps(df):
        if (df.iloc[3, -1] < 0 and df.iloc[3, -2] < 0 and df.iloc[3, -3] < 0 and df.iloc[3, -4] < 0):
            return 'True'
        else:
            return 'False'

    def dead_rev(df):
        if (df.iloc[1, -1] < 0 and df.iloc[1, -2] < 0 and df.iloc[1, -3] < 0 and df.iloc[1, -4] < 0):
            return 'True'
        else:
            return 'False'

    def dead_debt_cash(df):
        cash_securities = df.iloc[5, -1]
        debt = df.iloc[4, -1]
        if (debt / cash_securities >= 2):
            return 'True'
        else:
            return 'False'

    def dead_fcf(df):
        if (df.iloc[6, -1] < 0):
            return 'True'
        else:
            return 'False'

    def update_dead(df):
        df.iloc[0, 0] = dead_eps(quarterly_financials_df)
        df.iloc[1, 0] = dead_rev(quarterly_financials_df)
        df.iloc[2, 0] = dead_debt_cash(annual_financials_df)
        df.iloc[3, 0] = dead_fcf(annual_financials_df)
        return df

    # Fad Screen
    def fad_rev(df):
        if (df.iloc[1, -1] >= 39.5 and df.iloc[1, -2] >= 39.5 and df.iloc[1, -3] >= 39.5):
            return 'True'
        else:
            return 'False'

    def fad_eps(df):
        if (df.iloc[2, 1] > 0):
            return 'True'
        else:
            return 'False'

    def fad_eps_decline(df):
        if (df.iloc[3, -1] < 0):
            return 'True'
        else:
            return 'False'

    def update_fad(df):
        df.iloc[0, 0] = fad_rev(annual_financials_df)
        df.iloc[1, 0] = fad_eps(annual_financials_df)
        df.iloc[2, 0] = fad_eps_decline(annual_financials_df)
        return df

    # Hot Story Screen
    def hot_pe(df):
        if (df.iloc[3, 0] > 30):
            return 'True'
        else:
            return 'False'

    def update_hot(df):
        df.iloc[2, 0] = hot_pe(fundamental_df)
        return df

    # Display All Screens
    final_output = []

    s1 = update_fast_grower(fast_grower)
    s1 = s1.reset_index()

    s2 = update_stalwart(stalwart)
    s2 = s2.reset_index()

    s3 = update_surfer(surfer)
    s3 = s3.reset_index()

    s4 = update_dead(dead_walking)
    s4 = s4.reset_index()

    s5 = update_fad(fad)
    s5 = s5.reset_index()

    s6 = update_hot(hot_story)
    s6 = s6.reset_index()

    s7 = fundamental_df.reset_index()

    s8 = annual_financials_df.reset_index()

    s9 = quarterly_financials_df.reset_index()

    final_output.append(s1)
    final_output.append(s2)
    final_output.append(s3)
    final_output.append(s4)
    final_output.append(s5)
    final_output.append(s6)
    final_output.append(s7)
    final_output.append(s8)
    final_output.append(s9)

    return final_output
