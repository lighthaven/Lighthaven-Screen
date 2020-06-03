import pandas as pd

def execute(ticker):

    APIKEY = "8b2bf9e0d0fefa73a0b0c98b55bf82b3"
    try:
        try:
            # For Python 3.0 and later
            from urllib.request import urlopen
        except ImportError:
            # Fall back to Python 2's urllib2
            from urllib import urlopen

        import json

        def get_jsonparsed_data(url):
            response = urlopen(url)
            data = response.read().decode("utf-8")
            return json.loads(data)

        general = ("https://financialmodelingprep.com/api/v3/company/profile/" + ticker + '?apikey=' + APIKEY)
        a_financials_url = ("https://financialmodelingprep.com/api/v3/financials/income-statement/" + ticker + '?apikey=' + APIKEY)
        q_financials_url = ("https://financialmodelingprep.com/api/v3/financials/income-statement/"+ ticker +"?period=quarter" + '&apikey=' + APIKEY)
        q_balance_sheet_url = ('https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/' + ticker + '?period=quarter&apikey=' + APIKEY)
        balance_sheet_url = "https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/" + ticker + '?apikey=' + APIKEY
        cash_flow_url = "https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/" + ticker + '?apikey=' + APIKEY


        #Anual Financials Table
        try:
            a_financials = get_jsonparsed_data(a_financials_url)['financials']
            pd_annual = pd.DataFrame.from_dict(a_financials)[['date', 'Revenue', 'EPS Diluted']]
        except:
            return('Incorrect entry')


        balance_sheet = get_jsonparsed_data(balance_sheet_url)['financials']
        pd_balance = pd.DataFrame.from_dict(balance_sheet)[['date','Long-term debt', 'Cash and short-term investments']]
        combined = pd_annual.merge(pd_balance, left_on='date', right_on = 'date')

        rev = combined['Revenue']
        rev_growth = []
        eps = combined['EPS Diluted']
        eps_growth = []
        for i in range(len(rev)):
            try:
                x1 = (((float(rev[i]) - float(rev[i + 1])) / float(rev[i + 1]))*100)
                x2 = (((float(eps[i]) - float(eps[i + 1])) / float(eps[i + 1])) * 100)
                rev_growth.append(round(x1,2))
                eps_growth.append(round(x2,2))
            except:
                rev_growth.append('-')
                eps_growth.append('-')
        combined.insert(2, "Revenue Growth (%)", rev_growth, True)
        combined.insert(4, "EPS Growth (%)", eps_growth, True)




        fcf = get_jsonparsed_data(cash_flow_url)['financials']
        pd_fcf = pd.DataFrame.from_dict(fcf)[['date', 'Free Cash Flow']]
        combined_annual = combined.merge(pd_fcf, left_on = 'date', right_on = 'date').transpose()
        combined_annual = combined_annual.iloc[:,0:5]
        combined_annual = combined_annual[combined_annual.columns[::-1]]

        # Most recent Debt/Cash Numbers for DCM screen
        q_balance_sheet = get_jsonparsed_data(q_balance_sheet_url)['financials']
        recent_balance_sheet = pd.DataFrame.from_dict(q_balance_sheet)[['Long-term debt', 'Cash and short-term investments']].iloc[0]
        
        # # Quarterly Financials Table
        q_financials = get_jsonparsed_data(q_financials_url)['financials']
        pd_quarterly = pd.DataFrame.from_dict(q_financials)[['date', 'Revenue', 'EPS Diluted']]
        revenue_growth = []
        revs = pd_quarterly['Revenue']
        q_eps_growth = []
        q_eps = pd_quarterly['EPS Diluted']
        for i in range(len(revs)):
            try:
                x1 = (((float(revs[i])-float(revs[i+4]))/float(revs[i+4]))*100)
                x2 = (((float(q_eps[i]) - float(q_eps[i + 4])) / float(q_eps[i + 4]))*100)
                revenue_growth.append(round(x1,2))
                q_eps_growth.append(round(x2,2))
            except:
                revenue_growth.append('-')
                q_eps_growth.append('—')
        pd_quarterly.insert(2, "Revenue Growth (%)", revenue_growth, True)
        pd_quarterly.insert(4, "EPS Growth (%)", q_eps_growth, True)
        pd_quarterly.set_index('date')
        combined_quarterly = pd_quarterly.transpose().iloc[:,0:5]
        combined_quarterly = combined_quarterly[combined_quarterly.columns[::-1]]





        # Fundamental Data

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
            try:
                if (float(df.iloc[2, -1]) >= 14.5 and float(df.iloc[2, -2]) >= 14.5 and float(df.iloc[2, -3]) >= 14.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def fast_eps(df):
            try:
                if (float(df.iloc[4, -1]) >= 14.5 and float(df.iloc[4, -2]) >= 14.5 and float(df.iloc[4, -3]) >= 14.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def fast_debt_cash(df):
            try:
                cash_securities = float(df.iloc[6, -1])
                debt = float(df.iloc[5, -1])
                if (debt / cash_securities <= 2):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def fast_fcf(df):
            try:
                if (float(df.iloc[7, -1]) > 0 and float(df.iloc[7, -2]) > 0 and float(df.iloc[7, -3]) > 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def update_fast_grower(df):
            df.iloc[0, 0] = fast_rev(combined_annual)
            df.iloc[1, 0] = fast_eps(combined_annual)
            df.iloc[2, 0] = fast_debt_cash(combined_annual)
            df.iloc[3, 0] = fast_fcf(combined_annual)
            return df

        # Stalwart Screen
        def stalwart_rev(df):
            try:
                if (float(df.iloc[2, -1]) >= 9.5 and float(df.iloc[2, -2]) >= 9.5 and float(df.iloc[2, -3]) >= 9.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def stalwart_eps(df):
            try:
                if (float(df.iloc[4, -1]) >= 9.5 and float(df.iloc[4, -2]) >= 9.5 and float(df.iloc[4, -3]) >= 9.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def stalwart_market_cap(df):
            try:
                if (float(df.iloc[2, 0]) >= 100):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def update_stalwart(df):
            df.iloc[0, 0] = stalwart_rev(combined_annual)
            df.iloc[1, 0] = stalwart_eps(combined_annual)
            df.iloc[2, 0] = stalwart_market_cap(fundamental_df)
            return df

        # Surfer Screen
        def surfer_rev(df):
            try:
                if (float(df.iloc[2, -1]) >= 34.5 and float(df.iloc[2, -2]) >= 34.5 and float(df.iloc[2, -3]) >= 34.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def update_surfer(df):
            df.iloc[0, 0] = surfer_rev(combined_annual)
            return df

        # Dead Walking Screen
        def dead_eps(df):
            try:
                if (float(df.iloc[4, -1]) < 0 and float(df.iloc[4, -2]) < 0 and float(df.iloc[4, -3]) < 0 and float(df.iloc[4, -4]) < 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def dead_rev(df):
            try:
                if (float(df.iloc[2, -1]) < 0 and float(df.iloc[2, -2]) < 0 and float(df.iloc[2, -3]) < 0 and float(df.iloc[2, -4]) < 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def dead_debt_cash(df):
            try:
                cash_securities = float(df['Cash and short-term investments'])
                debt = float(df['Long-term debt'])
                if (debt / cash_securities >= 2):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def dead_fcf(df):
            try:
                if (float(df.iloc[7, -1]) < 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def update_dead(df):
            df.iloc[0, 0] = dead_eps(combined_quarterly)
            df.iloc[1, 0] = dead_rev(combined_quarterly)
            df.iloc[2, 0] = dead_debt_cash(recent_balance_sheet)
            df.iloc[3, 0] = dead_fcf(combined_annual)
            return df

        # Fad Screen
        def fad_rev(df):
            try:
                if (float(df.iloc[2, -1]) >= 39.5 and float(df.iloc[2, -2]) >= 39.5 and float(df.iloc[2, -3]) >= 39.5):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def fad_eps(df):
            try:
                if (float(df.iloc[3, 1]) > 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def fad_eps_decline(df):
            try:
                if (float(df.iloc[4, -1]) < 0):
                    return 'True'
                else:
                    return 'False'
            except:
                return 'False'

        def update_fad(df):
            df.iloc[0, 0] = fad_rev(combined_annual)
            df.iloc[1, 0] = fad_eps(combined_annual)
            df.iloc[2, 0] = fad_eps_decline(combined_annual)
            return df

        # Hot Story Screen
        def hot_pe(df):
            try:
                if (float(df.iloc[3, 0]) > 30):
                    return 'True'
                else:
                    return 'False'
            except:
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

        s7 = fundamental_df
        s7 = s7.reset_index()


        combined_annual.iloc[1] = combined_annual.iloc[1].astype(float) / 1000000
        combined_annual.iloc[5] = combined_annual.iloc[5].astype(float) / 1000000
        combined_annual.iloc[6] = combined_annual.iloc[6].astype(float) / 1000000
        combined_annual.iloc[7] = combined_annual.iloc[7].astype(float) / 1000000


        s8 = combined_annual.transpose().set_index('date').transpose()
        s8 = s8.reset_index()
        s8.rename(columns={'index': 'Metric'}, inplace=True)

        #cleaning combined_quarterly
        combined_quarterly.iloc[1] = combined_quarterly.iloc[1].astype(float) / 1000000
        s9 = combined_quarterly.transpose().set_index('date').transpose()
        s9 = s9.reset_index()
        s9.rename(columns={'index':'Metric'}, inplace=True)

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
    except:
        return ('There was an error somewhere above')
