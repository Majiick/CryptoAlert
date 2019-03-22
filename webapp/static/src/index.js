import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label, Menu, List, Header, Container, Divider, Input, Segment, TransitionablePortal, Dropdown, Grid, Checkbox } from 'semantic-ui-react'
import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux';
import ReactTable from "react-table";
import 'react-table/react-table.css'
import './styles.css';
import { CSSTransitionGroup } from 'react-transition-group'

const belowAboveOptions = [
          { key: 'above', text: 'Above', value: 'above' },
          { key: 'below', text: 'Below', value: 'below' }
        ];

const upDownOptions = [
          { key: 'above', text: 'Up', value: 'above' },
          { key: 'below', text: 'Down', value: 'below' }
        ];

const exchangeOptions = [
            { key: 'POLONIEX', text: 'Poloniex', value: 'POLONIEX' },
            { key: 'BITTREX', text: 'Bittrex', value: 'BITTREX' },
            { key: '*', text: 'All', value: '*' }
        ];

const pairOptions = [
    { key: '*', text: 'All', value: '*' },
    {key: 'BTC_STORM', text: 'BTC_STORM', value: 'BTC_STORM'},
    {key: 'BTC_BURST', text: 'BTC_BURST', value: 'BTC_BURST'},
    {key: 'BTC_BSV', text: 'BTC_BSV', value: 'BTC_BSV'},
    {key: 'USDT_NXT', text: 'USDT_NXT', value: 'USDT_NXT'},
    {key: 'BTC_ABY', text: 'BTC_ABY', value: 'BTC_ABY'},
    {key: 'BTC_NLC2', text: 'BTC_NLC2', value: 'BTC_NLC2'},
    {key: 'ETH_MCO', text: 'ETH_MCO', value: 'ETH_MCO'},
    {key: 'BTC_RVN', text: 'BTC_RVN', value: 'BTC_RVN'},
    {key: 'USD_ETH', text: 'USD_ETH', value: 'USD_ETH'},
    {key: 'BTC_CBC', text: 'BTC_CBC', value: 'BTC_CBC'},
    {key: 'USDT_OMG', text: 'USDT_OMG', value: 'USDT_OMG'},
    {key: 'BTC_BAT', text: 'BTC_BAT', value: 'BTC_BAT'},
    {key: 'BTC_BLK', text: 'BTC_BLK', value: 'BTC_BLK'},
    {key: 'BTC_DYN', text: 'BTC_DYN', value: 'BTC_DYN'},
    {key: 'BTC_STR', text: 'BTC_STR', value: 'BTC_STR'},
    {key: 'BTC_SIB', text: 'BTC_SIB', value: 'BTC_SIB'},
    {key: 'BTC_OMNI', text: 'BTC_OMNI', value: 'BTC_OMNI'},
    {key: 'ETH_SRN', text: 'ETH_SRN', value: 'ETH_SRN'},
    {key: 'BTC_SBD', text: 'BTC_SBD', value: 'BTC_SBD'},
    {key: 'USDT_XVG', text: 'USDT_XVG', value: 'USDT_XVG'},
    {key: 'BTC_XST', text: 'BTC_XST', value: 'BTC_XST'},
    {key: 'USDT_LSK', text: 'USDT_LSK', value: 'USDT_LSK'},
    {key: 'USD_EDR', text: 'USD_EDR', value: 'USD_EDR'},
    {key: 'BTC_SPHR', text: 'BTC_SPHR', value: 'BTC_SPHR'},
    {key: 'BTC_DGB', text: 'BTC_DGB', value: 'BTC_DGB'},
    {key: 'BTC_PINK', text: 'BTC_PINK', value: 'BTC_PINK'},
    {key: 'BTC_ETH', text: 'BTC_ETH', value: 'BTC_ETH'},
    {key: 'BTC_KMD', text: 'BTC_KMD', value: 'BTC_KMD'},
    {key: 'USDT_ETC', text: 'USDT_ETC', value: 'USDT_ETC'},
    {key: 'BTC_LBC', text: 'BTC_LBC', value: 'BTC_LBC'},
    {key: 'BTC_2GIVE', text: 'BTC_2GIVE', value: 'BTC_2GIVE'},
    {key: 'BTC_AID', text: 'BTC_AID', value: 'BTC_AID'},
    {key: 'BTC_BSD', text: 'BTC_BSD', value: 'BTC_BSD'},
    {key: 'USDT_ZRX', text: 'USDT_ZRX', value: 'USDT_ZRX'},
    {key: 'ETH_DMT', text: 'ETH_DMT', value: 'ETH_DMT'},
    {key: 'USDT_BNT', text: 'USDT_BNT', value: 'USDT_BNT'},
    {key: 'BTC_THC', text: 'BTC_THC', value: 'BTC_THC'},
    {key: 'BTC_OK', text: 'BTC_OK', value: 'BTC_OK'},
    {key: 'BTC_NXC', text: 'BTC_NXC', value: 'BTC_NXC'},
    {key: 'ETH_GNT', text: 'ETH_GNT', value: 'ETH_GNT'},
    {key: 'BTC_IOP', text: 'BTC_IOP', value: 'BTC_IOP'},
    {key: 'BTC_RFR', text: 'BTC_RFR', value: 'BTC_RFR'},
    {key: 'USDT_ADA', text: 'USDT_ADA', value: 'USDT_ADA'},
    {key: 'BTC_STEEM', text: 'BTC_STEEM', value: 'BTC_STEEM'},
    {key: 'BTC_DNT', text: 'BTC_DNT', value: 'BTC_DNT'},
    {key: 'USD_BTC', text: 'USD_BTC', value: 'USD_BTC'},
    {key: 'BTC_SNT', text: 'BTC_SNT', value: 'BTC_SNT'},
    {key: 'ETH_ZRX', text: 'ETH_ZRX', value: 'ETH_ZRX'},
    {key: 'ETH_SOLVE', text: 'ETH_SOLVE', value: 'ETH_SOLVE'},
    {key: 'USDT_XMR', text: 'USDT_XMR', value: 'USDT_XMR'},
    {key: 'USD_PAX', text: 'USD_PAX', value: 'USD_PAX'},
    {key: 'ETH_ANT', text: 'ETH_ANT', value: 'ETH_ANT'},
    {key: 'BTC_MER', text: 'BTC_MER', value: 'BTC_MER'},
    {key: 'ETH_VIB', text: 'ETH_VIB', value: 'ETH_VIB'},
    {key: 'BTC_MTL', text: 'BTC_MTL', value: 'BTC_MTL'},
    {key: 'USDT_SNT', text: 'USDT_SNT', value: 'USDT_SNT'},
    {key: 'BTC_QRL', text: 'BTC_QRL', value: 'BTC_QRL'},
    {key: 'USDT_GNT', text: 'USDT_GNT', value: 'USDT_GNT'},
    {key: 'BTC_EOS', text: 'BTC_EOS', value: 'BTC_EOS'},
    {key: 'BTC_NEOS', text: 'BTC_NEOS', value: 'BTC_NEOS'},
    {key: 'BTC_MOBI', text: 'BTC_MOBI', value: 'BTC_MOBI'},
    {key: 'ETH_XLM', text: 'ETH_XLM', value: 'ETH_XLM'},
    {key: 'BTC_HMQ', text: 'BTC_HMQ', value: 'BTC_HMQ'},
    {key: 'USDT_DASH', text: 'USDT_DASH', value: 'USDT_DASH'},
    {key: 'BTC_XZC', text: 'BTC_XZC', value: 'BTC_XZC'},
    {key: 'BTC_EXCL', text: 'BTC_EXCL', value: 'BTC_EXCL'},
    {key: 'BTC_ZCL', text: 'BTC_ZCL', value: 'BTC_ZCL'},
    {key: 'BTC_NMR', text: 'BTC_NMR', value: 'BTC_NMR'},
    {key: 'BTC_IHT', text: 'BTC_IHT', value: 'BTC_IHT'},
    {key: 'ETH_CVC', text: 'ETH_CVC', value: 'ETH_CVC'},
    {key: 'ETH_XMR', text: 'ETH_XMR', value: 'ETH_XMR'},
    {key: 'XMR_BCN', text: 'XMR_BCN', value: 'XMR_BCN'},
    {key: 'BTC_MUSIC', text: 'BTC_MUSIC', value: 'BTC_MUSIC'},
    {key: 'USDT_ZEC', text: 'USDT_ZEC', value: 'USDT_ZEC'},
    {key: 'ETH_GAS', text: 'ETH_GAS', value: 'ETH_GAS'},
    {key: 'BTC_IOC', text: 'BTC_IOC', value: 'BTC_IOC'},
    {key: 'BTC_ANT', text: 'BTC_ANT', value: 'BTC_ANT'},
    {key: 'BTC_ZRX', text: 'BTC_ZRX', value: 'BTC_ZRX'},
    {key: 'BTC_NEO', text: 'BTC_NEO', value: 'BTC_NEO'},
    {key: 'BTC_DMD', text: 'BTC_DMD', value: 'BTC_DMD'},
    {key: 'BTC_UPP', text: 'BTC_UPP', value: 'BTC_UPP'},
    {key: 'BTC_BTS', text: 'BTC_BTS', value: 'BTC_BTS'},
    {key: 'BTC_BITB', text: 'BTC_BITB', value: 'BTC_BITB'},
    {key: 'BTC_GLC', text: 'BTC_GLC', value: 'BTC_GLC'},
    {key: 'USDT_SC', text: 'USDT_SC', value: 'USDT_SC'},
    {key: 'BTC_FCT', text: 'BTC_FCT', value: 'BTC_FCT'},
    {key: 'BTC_VIB', text: 'BTC_VIB', value: 'BTC_VIB'},
    {key: 'BTC_EGC', text: 'BTC_EGC', value: 'BTC_EGC'},
    {key: 'BTC_MUE', text: 'BTC_MUE', value: 'BTC_MUE'},
    {key: 'BTC_EDR', text: 'BTC_EDR', value: 'BTC_EDR'},
    {key: 'BTC_LUN', text: 'BTC_LUN', value: 'BTC_LUN'},
    {key: 'BTC_QTUM', text: 'BTC_QTUM', value: 'BTC_QTUM'},
    {key: 'BTC_GAM', text: 'BTC_GAM', value: 'BTC_GAM'},
    {key: 'BTC_COVAL', text: 'BTC_COVAL', value: 'BTC_COVAL'},
    {key: 'USDT_NEO', text: 'USDT_NEO', value: 'USDT_NEO'},
    {key: 'BTC_NGC', text: 'BTC_NGC', value: 'BTC_NGC'},
    {key: 'BTC_BRK', text: 'BTC_BRK', value: 'BTC_BRK'},
    {key: 'BTC_SHIFT', text: 'BTC_SHIFT', value: 'BTC_SHIFT'},
    {key: 'BTC_NMC', text: 'BTC_NMC', value: 'BTC_NMC'},
    {key: 'BTC_SYNX', text: 'BTC_SYNX', value: 'BTC_SYNX'},
    {key: 'BTC_HYDRO', text: 'BTC_HYDRO', value: 'BTC_HYDRO'},
    {key: 'BTC_FLDC', text: 'BTC_FLDC', value: 'BTC_FLDC'},
    {key: 'BTC_POWR', text: 'BTC_POWR', value: 'BTC_POWR'},
    {key: 'ETH_WAVES', text: 'ETH_WAVES', value: 'ETH_WAVES'},
    {key: 'BTC_KORE', text: 'BTC_KORE', value: 'BTC_KORE'},
    {key: 'ETH_TUSD', text: 'ETH_TUSD', value: 'ETH_TUSD'},
    {key: 'ETH_POWR', text: 'ETH_POWR', value: 'ETH_POWR'},
    {key: 'BTC_GBYTE', text: 'BTC_GBYTE', value: 'BTC_GBYTE'},
    {key: 'BTC_STRAT', text: 'BTC_STRAT', value: 'BTC_STRAT'},
    {key: 'XMR_MAID', text: 'XMR_MAID', value: 'XMR_MAID'},
    {key: 'USD_SC', text: 'USD_SC', value: 'USD_SC'},
    {key: 'BTC_RVR', text: 'BTC_RVR', value: 'BTC_RVR'},
    {key: 'ETH_ADA', text: 'ETH_ADA', value: 'ETH_ADA'},
    {key: 'BTC_STORJ', text: 'BTC_STORJ', value: 'BTC_STORJ'},
    {key: 'ETH_STRAT', text: 'ETH_STRAT', value: 'ETH_STRAT'},
    {key: 'USD_XRP', text: 'USD_XRP', value: 'USD_XRP'},
    {key: 'ETH_GNO', text: 'ETH_GNO', value: 'ETH_GNO'},
    {key: 'USDT_DCR', text: 'USDT_DCR', value: 'USDT_DCR'},
    {key: 'USDT_QTUM', text: 'USDT_QTUM', value: 'USDT_QTUM'},
    {key: 'BTC_INCNT', text: 'BTC_INCNT', value: 'BTC_INCNT'},
    {key: 'USDT_PAX', text: 'USDT_PAX', value: 'USDT_PAX'},
    {key: 'USD_DGB', text: 'USD_DGB', value: 'USD_DGB'},
    {key: 'USDC_USDT', text: 'USDC_USDT', value: 'USDC_USDT'},
    {key: 'ETH_NEO', text: 'ETH_NEO', value: 'ETH_NEO'},
    {key: 'BTC_MAID', text: 'BTC_MAID', value: 'BTC_MAID'},
    {key: 'BTC_MOC', text: 'BTC_MOC', value: 'BTC_MOC'},
    {key: 'ETH_BNT', text: 'ETH_BNT', value: 'ETH_BNT'},
    {key: 'USDT_EOS', text: 'USDT_EOS', value: 'USDT_EOS'},
    {key: 'USD_BSV', text: 'USD_BSV', value: 'USD_BSV'},
    {key: 'USD_ZEC', text: 'USD_ZEC', value: 'USD_ZEC'},
    {key: 'BTC_BCPT', text: 'BTC_BCPT', value: 'BTC_BCPT'},
    {key: 'BTC_DMT', text: 'BTC_DMT', value: 'BTC_DMT'},
    {key: 'BTC_LTC', text: 'BTC_LTC', value: 'BTC_LTC'},
    {key: 'USDT_STR', text: 'USDT_STR', value: 'USDT_STR'},
    {key: 'BTC_RLC', text: 'BTC_RLC', value: 'BTC_RLC'},
    {key: 'BTC_LSK', text: 'BTC_LSK', value: 'BTC_LSK'},
    {key: 'ETH_WAX', text: 'ETH_WAX', value: 'ETH_WAX'},
    {key: 'XMR_DASH', text: 'XMR_DASH', value: 'XMR_DASH'},
    {key: 'BTC_BOXX', text: 'BTC_BOXX', value: 'BTC_BOXX'},
    {key: 'BTC_UP', text: 'BTC_UP', value: 'BTC_UP'},
    {key: 'BTC_GRC', text: 'BTC_GRC', value: 'BTC_GRC'},
    {key: 'BTC_FTC', text: 'BTC_FTC', value: 'BTC_FTC'},
    {key: 'BTC_MONA', text: 'BTC_MONA', value: 'BTC_MONA'},
    {key: 'BTC_ARDR', text: 'BTC_ARDR', value: 'BTC_ARDR'},
    {key: 'USDT_MANA', text: 'USDT_MANA', value: 'USDT_MANA'},
    {key: 'BTC_TKS', text: 'BTC_TKS', value: 'BTC_TKS'},
    {key: 'BTC_BTM', text: 'BTC_BTM', value: 'BTC_BTM'},
    {key: 'BTC_XLM', text: 'BTC_XLM', value: 'BTC_XLM'},
    {key: 'BTC_ARK', text: 'BTC_ARK', value: 'BTC_ARK'},
    {key: 'BTC_IGNIS', text: 'BTC_IGNIS', value: 'BTC_IGNIS'},
    {key: 'BTC_VRM', text: 'BTC_VRM', value: 'BTC_VRM'},
    {key: 'ETH_UKG', text: 'ETH_UKG', value: 'ETH_UKG'},
    {key: 'USD_LTC', text: 'USD_LTC', value: 'USD_LTC'},
    {key: 'ETH_XRP', text: 'ETH_XRP', value: 'ETH_XRP'},
    {key: 'USD_ZRX', text: 'USD_ZRX', value: 'USD_ZRX'},
    {key: 'BTC_HUC', text: 'BTC_HUC', value: 'BTC_HUC'},
    {key: 'USD_USDT', text: 'USD_USDT', value: 'USD_USDT'},
    {key: 'BTC_ENJ', text: 'BTC_ENJ', value: 'BTC_ENJ'},
    {key: 'ETH_TRX', text: 'ETH_TRX', value: 'ETH_TRX'},
    {key: 'BTC_AMP', text: 'BTC_AMP', value: 'BTC_AMP'},
    {key: 'ETH_DASH', text: 'ETH_DASH', value: 'ETH_DASH'},
    {key: 'BTC_EDG', text: 'BTC_EDG', value: 'BTC_EDG'},
    {key: 'ETH_DGB', text: 'ETH_DGB', value: 'ETH_DGB'},
    {key: 'ETH_ZEC', text: 'ETH_ZEC', value: 'ETH_ZEC'},
    {key: 'BTC_XDN', text: 'BTC_XDN', value: 'BTC_XDN'},
    {key: 'BTC_GNT', text: 'BTC_GNT', value: 'BTC_GNT'},
    {key: 'BTC_CANN', text: 'BTC_CANN', value: 'BTC_CANN'},
    {key: 'USDT_KNC', text: 'USDT_KNC', value: 'USDT_KNC'},
    {key: 'BTC_PAL', text: 'BTC_PAL', value: 'BTC_PAL'},
    {key: 'BTC_VEE', text: 'BTC_VEE', value: 'BTC_VEE'},
    {key: 'BTC_ADA', text: 'BTC_ADA', value: 'BTC_ADA'},
    {key: 'BTC_SLS', text: 'BTC_SLS', value: 'BTC_SLS'},
    {key: 'BTC_TUBE', text: 'BTC_TUBE', value: 'BTC_TUBE'},
    {key: 'USDT_RVN', text: 'USDT_RVN', value: 'USDT_RVN'},
    {key: 'BTC_GAME', text: 'BTC_GAME', value: 'BTC_GAME'},
    {key: 'BTC_CLAM', text: 'BTC_CLAM', value: 'BTC_CLAM'},
    {key: 'BTC_DOGE', text: 'BTC_DOGE', value: 'BTC_DOGE'},
    {key: 'BTC_LBA', text: 'BTC_LBA', value: 'BTC_LBA'},
    {key: 'BTC_BAY', text: 'BTC_BAY', value: 'BTC_BAY'},
    {key: 'USDT_BCH', text: 'USDT_BCH', value: 'USDT_BCH'},
    {key: 'BTC_PAX', text: 'BTC_PAX', value: 'BTC_PAX'},
    {key: 'BTC_PAY', text: 'BTC_PAY', value: 'BTC_PAY'},
    {key: 'BTC_EXP', text: 'BTC_EXP', value: 'BTC_EXP'},
    {key: 'BTC_WAVES', text: 'BTC_WAVES', value: 'BTC_WAVES'},
    {key: 'USD_TUSD', text: 'USD_TUSD', value: 'USD_TUSD'},
    {key: 'USDT_BTC', text: 'USDT_BTC', value: 'USDT_BTC'},
    {key: 'BTC_SRN', text: 'BTC_SRN', value: 'BTC_SRN'},
    {key: 'BTC_LOOM', text: 'BTC_LOOM', value: 'BTC_LOOM'},
    {key: 'BTC_BCH', text: 'BTC_BCH', value: 'BTC_BCH'},
    {key: 'XMR_NXT', text: 'XMR_NXT', value: 'XMR_NXT'},
    {key: 'USDT_ETH', text: 'USDT_ETH', value: 'USDT_ETH'},
    {key: 'USD_SPND', text: 'USD_SPND', value: 'USD_SPND'},
    {key: 'BTC_UBQ', text: 'BTC_UBQ', value: 'BTC_UBQ'},
    {key: 'USDT_DGB', text: 'USDT_DGB', value: 'USDT_DGB'},
    {key: 'USDT_XLM', text: 'USDT_XLM', value: 'USDT_XLM'},
    {key: 'BTC_DCT', text: 'BTC_DCT', value: 'BTC_DCT'},
    {key: 'USDC_BTC', text: 'USDC_BTC', value: 'USDC_BTC'},
    {key: 'ETH_OMG', text: 'ETH_OMG', value: 'ETH_OMG'},
    {key: 'BTC_QWARK', text: 'BTC_QWARK', value: 'BTC_QWARK'},
    {key: 'BTC_XEL', text: 'BTC_XEL', value: 'BTC_XEL'},
    {key: 'BTC_PMA', text: 'BTC_PMA', value: 'BTC_PMA'},
    {key: 'BTC_GO', text: 'BTC_GO', value: 'BTC_GO'},
    {key: 'BTC_ZEN', text: 'BTC_ZEN', value: 'BTC_ZEN'},
    {key: 'BTC_BNT', text: 'BTC_BNT', value: 'BTC_BNT'},
    {key: 'BTC_SALT', text: 'BTC_SALT', value: 'BTC_SALT'},
    {key: 'BTC_NAV', text: 'BTC_NAV', value: 'BTC_NAV'},
    {key: 'BTC_PART', text: 'BTC_PART', value: 'BTC_PART'},
    {key: 'BTC_MEME', text: 'BTC_MEME', value: 'BTC_MEME'},
    {key: 'ETH_STORM', text: 'ETH_STORM', value: 'ETH_STORM'},
    {key: 'BTC_XEM', text: 'BTC_XEM', value: 'BTC_XEM'},
    {key: 'USD_ADA', text: 'USD_ADA', value: 'USD_ADA'},
    {key: 'BTC_XCP', text: 'BTC_XCP', value: 'BTC_XCP'},
    {key: 'BTC_CRW', text: 'BTC_CRW', value: 'BTC_CRW'},
    {key: 'USD_KMD', text: 'USD_KMD', value: 'USD_KMD'},
    {key: 'BTC_GAS', text: 'BTC_GAS', value: 'BTC_GAS'},
    {key: 'USDT_TUSD', text: 'USDT_TUSD', value: 'USDT_TUSD'},
    {key: 'BTC_RDD', text: 'BTC_RDD', value: 'BTC_RDD'},
    {key: 'BTC_CURE', text: 'BTC_CURE', value: 'BTC_CURE'},
    {key: 'BTC_ION', text: 'BTC_ION', value: 'BTC_ION'},
    {key: 'BTC_ZEC', text: 'BTC_ZEC', value: 'BTC_ZEC'},
    {key: 'USD_BAT', text: 'USD_BAT', value: 'USD_BAT'},
    {key: 'BTC_PASC', text: 'BTC_PASC', value: 'BTC_PASC'},
    {key: 'USDT_BAT', text: 'USDT_BAT', value: 'USDT_BAT'},
    {key: 'BTC_POT', text: 'BTC_POT', value: 'BTC_POT'},
    {key: 'ETH_SNT', text: 'ETH_SNT', value: 'ETH_SNT'},
    {key: 'BTC_REP', text: 'BTC_REP', value: 'BTC_REP'},
    {key: 'BTC_XMY', text: 'BTC_XMY', value: 'BTC_XMY'},
    {key: 'ETH_ENG', text: 'ETH_ENG', value: 'ETH_ENG'},
    {key: 'ETH_POLY', text: 'ETH_POLY', value: 'ETH_POLY'},
    {key: 'XMR_ZEC', text: 'XMR_ZEC', value: 'XMR_ZEC'},
    {key: 'USDT_PMA', text: 'USDT_PMA', value: 'USDT_PMA'},
    {key: 'ETH_QTUM', text: 'ETH_QTUM', value: 'ETH_QTUM'},
    {key: 'USDT_LTC', text: 'USDT_LTC', value: 'USDT_LTC'},
    {key: 'BTC_WAX', text: 'BTC_WAX', value: 'BTC_WAX'},
    {key: 'BTC_GNO', text: 'BTC_GNO', value: 'BTC_GNO'},
    {key: 'ETH_SC', text: 'ETH_SC', value: 'ETH_SC'},
    {key: 'BTC_LRC', text: 'BTC_LRC', value: 'BTC_LRC'},
    {key: 'BTC_NBT', text: 'BTC_NBT', value: 'BTC_NBT'},
    {key: 'BTC_GEO', text: 'BTC_GEO', value: 'BTC_GEO'},
    {key: 'BTC_EMC2', text: 'BTC_EMC2', value: 'BTC_EMC2'},
    {key: 'BTC_SYS', text: 'BTC_SYS', value: 'BTC_SYS'},
    {key: 'BTC_RCN', text: 'BTC_RCN', value: 'BTC_RCN'},
    {key: 'ETH_ETC', text: 'ETH_ETC', value: 'ETH_ETC'},
    {key: 'BTC_SPND', text: 'BTC_SPND', value: 'BTC_SPND'},
    {key: 'BTC_OCN', text: 'BTC_OCN', value: 'BTC_OCN'},
    {key: 'BTC_CMCT', text: 'BTC_CMCT', value: 'BTC_CMCT'},
    {key: 'BTC_KNC', text: 'BTC_KNC', value: 'BTC_KNC'},
    {key: 'ETH_MANA', text: 'ETH_MANA', value: 'ETH_MANA'},
    {key: 'BTC_GOLOS', text: 'BTC_GOLOS', value: 'BTC_GOLOS'},
    {key: 'ETH_STEEM', text: 'ETH_STEEM', value: 'ETH_STEEM'},
    {key: 'BTC_GRS', text: 'BTC_GRS', value: 'BTC_GRS'},
    {key: 'BTC_XPM', text: 'BTC_XPM', value: 'BTC_XPM'},
    {key: 'USDT_DOGE', text: 'USDT_DOGE', value: 'USDT_DOGE'},
    {key: 'BTC_EMC', text: 'BTC_EMC', value: 'BTC_EMC'},
    {key: 'BTC_OMG', text: 'BTC_OMG', value: 'BTC_OMG'},
    {key: 'ETH_LTC', text: 'ETH_LTC', value: 'ETH_LTC'},
    {key: 'ETH_PAY', text: 'ETH_PAY', value: 'ETH_PAY'},
    {key: 'BTC_DTB', text: 'BTC_DTB', value: 'BTC_DTB'},
    {key: 'BTC_TUSD', text: 'BTC_TUSD', value: 'BTC_TUSD'},
    {key: 'BTC_BLOCK', text: 'BTC_BLOCK', value: 'BTC_BLOCK'},
    {key: 'USDT_LOOM', text: 'USDT_LOOM', value: 'USDT_LOOM'},
    {key: 'BTC_TIX', text: 'BTC_TIX', value: 'BTC_TIX'},
    {key: 'USD_ZEN', text: 'USD_ZEN', value: 'USD_ZEN'},
    {key: 'USDC_ETH', text: 'USDC_ETH', value: 'USDC_ETH'},
    {key: 'BTC_FLO', text: 'BTC_FLO', value: 'BTC_FLO'},
    {key: 'BTC_MFT', text: 'BTC_MFT', value: 'BTC_MFT'},
    {key: 'BTC_VIA', text: 'BTC_VIA', value: 'BTC_VIA'},
    {key: 'BTC_RADS', text: 'BTC_RADS', value: 'BTC_RADS'},
    {key: 'BTC_ADT', text: 'BTC_ADT', value: 'BTC_ADT'},
    {key: 'BTC_SWT', text: 'BTC_SWT', value: 'BTC_SWT'},
    {key: 'BTC_ENG', text: 'BTC_ENG', value: 'BTC_ENG'},
    {key: 'BTC_BRX', text: 'BTC_BRX', value: 'BTC_BRX'},
    {key: 'BTC_PPC', text: 'BTC_PPC', value: 'BTC_PPC'},
    {key: 'BTC_NLG', text: 'BTC_NLG', value: 'BTC_NLG'},
    {key: 'BTC_BKX', text: 'BTC_BKX', value: 'BTC_BKX'},
    {key: 'USDT_XRP', text: 'USDT_XRP', value: 'USDT_XRP'},
    {key: 'BTC_XVG', text: 'BTC_XVG', value: 'BTC_XVG'},
    {key: 'BTC_CVC', text: 'BTC_CVC', value: 'BTC_CVC'},
    {key: 'BTC_UKG', text: 'BTC_UKG', value: 'BTC_UKG'},
    {key: 'BTC_EBST', text: 'BTC_EBST', value: 'BTC_EBST'},
    {key: 'BTC_VTC', text: 'BTC_VTC', value: 'BTC_VTC'},
    {key: 'BTC_MCO', text: 'BTC_MCO', value: 'BTC_MCO'},
    {key: 'BTC_XHV', text: 'BTC_XHV', value: 'BTC_XHV'},
    {key: 'BTC_BCN', text: 'BTC_BCN', value: 'BTC_BCN'},
    {key: 'ETH_BAT', text: 'ETH_BAT', value: 'ETH_BAT'},
    {key: 'BTC_ETC', text: 'BTC_ETC', value: 'BTC_ETC'},
    {key: 'BTC_GTO', text: 'BTC_GTO', value: 'BTC_GTO'},
    {key: 'BTC_BFT', text: 'BTC_BFT', value: 'BTC_BFT'},
    {key: 'BTC_BITS', text: 'BTC_BITS', value: 'BTC_BITS'},
    {key: 'BTC_DASH', text: 'BTC_DASH', value: 'BTC_DASH'},
    {key: 'BTC_GUP', text: 'BTC_GUP', value: 'BTC_GUP'},
    {key: 'ETH_XEM', text: 'ETH_XEM', value: 'ETH_XEM'},
    {key: 'BTC_PRO', text: 'BTC_PRO', value: 'BTC_PRO'},
    {key: 'USDT_REP', text: 'USDT_REP', value: 'USDT_REP'},
    {key: 'BTC_SLR', text: 'BTC_SLR', value: 'BTC_SLR'},
    {key: 'ETH_OCN', text: 'ETH_OCN', value: 'ETH_OCN'},
    {key: 'BTC_TRX', text: 'BTC_TRX', value: 'BTC_TRX'},
    {key: 'BTC_PTOY', text: 'BTC_PTOY', value: 'BTC_PTOY'},
    {key: 'ETH_LSK', text: 'ETH_LSK', value: 'ETH_LSK'},
    {key: 'ETH_EOS', text: 'ETH_EOS', value: 'ETH_EOS'},
    {key: 'BTC_VRC', text: 'BTC_VRC', value: 'BTC_VRC'},
    {key: 'BTC_AEON', text: 'BTC_AEON', value: 'BTC_AEON'},
    {key: 'BTC_DCR', text: 'BTC_DCR', value: 'BTC_DCR'},
    {key: 'BTC_TX', text: 'BTC_TX', value: 'BTC_TX'},
    {key: 'BTC_SPC', text: 'BTC_SPC', value: 'BTC_SPC'},
    {key: 'BTC_SC', text: 'BTC_SC', value: 'BTC_SC'},
    {key: 'ETH_BCH', text: 'ETH_BCH', value: 'ETH_BCH'},
    {key: 'BTC_SEQ', text: 'BTC_SEQ', value: 'BTC_SEQ'},
    {key: 'USD_ETC', text: 'USD_ETC', value: 'USD_ETC'},
    {key: 'BTC_ADX', text: 'BTC_ADX', value: 'BTC_ADX'},
    {key: 'USD_BCH', text: 'USD_BCH', value: 'USD_BCH'},
    {key: 'BTC_MET', text: 'BTC_MET', value: 'BTC_MET'},
    {key: 'BTC_BLT', text: 'BTC_BLT', value: 'BTC_BLT'},
    {key: 'BTC_CLOAK', text: 'BTC_CLOAK', value: 'BTC_CLOAK'},
    {key: 'XMR_LTC', text: 'XMR_LTC', value: 'XMR_LTC'},
    {key: 'BTC_XWC', text: 'BTC_XWC', value: 'BTC_XWC'},
    {key: 'ETH_BSV', text: 'ETH_BSV', value: 'ETH_BSV'},
    {key: 'BTC_DOPE', text: 'BTC_DOPE', value: 'BTC_DOPE'},
    {key: 'BTC_NXT', text: 'BTC_NXT', value: 'BTC_NXT'},
    {key: 'USD_USDS', text: 'USD_USDS', value: 'USD_USDS'},
    {key: 'USDT_BSV', text: 'USDT_BSV', value: 'USDT_BSV'},
    {key: 'BTC_POLY', text: 'BTC_POLY', value: 'BTC_POLY'},
    {key: 'BTC_XRP', text: 'BTC_XRP', value: 'BTC_XRP'},
    {key: 'ETH_ADX', text: 'ETH_ADX', value: 'ETH_ADX'},
    {key: 'BTC_USDS', text: 'BTC_USDS', value: 'BTC_USDS'},
    {key: 'BTC_XNK', text: 'BTC_XNK', value: 'BTC_XNK'},
    {key: 'BTC_SOLVE', text: 'BTC_SOLVE', value: 'BTC_SOLVE'},
    {key: 'USDT_TRX', text: 'USDT_TRX', value: 'USDT_TRX'},
    {key: 'BTC_PIVX', text: 'BTC_PIVX', value: 'BTC_PIVX'},
    {key: 'BTC_XMR', text: 'BTC_XMR', value: 'BTC_XMR'},
    {key: 'BTC_MLN', text: 'BTC_MLN', value: 'BTC_MLN'},
    {key: 'BTC_GBG', text: 'BTC_GBG', value: 'BTC_GBG'},
    {key: 'BTC_MANA', text: 'BTC_MANA', value: 'BTC_MANA'},
    {key: 'BTC_DTA', text: 'BTC_DTA', value: 'BTC_DTA'},
    {key: 'USD_TRX', text: 'USD_TRX', value: 'USD_TRX'},
    {key: 'BTC_WINGS', text: 'BTC_WINGS', value: 'BTC_WINGS'},
    {key: 'BTC_NXS', text: 'BTC_NXS', value: 'BTC_NXS'},
    {key: 'BTC_MORE', text: 'BTC_MORE', value: 'BTC_MORE'},
    {key: 'ETH_LOOM', text: 'ETH_LOOM', value: 'ETH_LOOM'},
    {key: 'ETH_REP', text: 'ETH_REP', value: 'ETH_REP'},
    {key: 'ETH_KNC', text: 'ETH_KNC', value: 'ETH_KNC'}
];

const reduxState = {
    jwt_token: '',
    updateMyAlerts: false,
    user_email: '',
    email_notification_value: false
}

function reduxReducer(state, action) {
  if (typeof state === 'undefined') {
    return reduxState;
  }

  switch (action.type) {
      case "JWTTOKEN":
          state['jwt_token'] = action.token;
          console.log('jwt token updated');
          return state;
      case "TOPMENUSELECTION":
          state['topMenuSelection'] = action.selection;
	      console.log('top menu selection dispatched selection: ' + action.selection);
          return state;
      case "UPDATEMYALERTS":
          state['updateMyAlerts'] = action.update;
          console.log('Update my alerts updated to: ' + action.update);
	      return state;
      case "SETUSEREMAIL":
          state['user_email'] = action.email;
          return state;
      case "SETEMAILNOTIFICATIONVALUE":
          console.log('Set action.email_notification_value to ' + action.email_notification_value)
          state['email_notification_value'] = action.email_notification_value;
          return state;
      default:
          console.warn('Default redux action, state not changed, action.');
          console.warn(action);
          return state;
  }

  return state;
}

const reduxStore = createStore(reduxReducer);

function component() {
	let element = document.createElement('div');

	element.innerHTML = _.join(['xD', 'socketio'], ' ');
	return element;
}

class AlertsButton extends React.Component {
    constructor(props) {
        super(props);
      }

    render() {
      return (
          <div>
                <Button as='div' labelPosition='right'>
                    <Button color='red'>
                        <Icon name='exclamation triangle' />
                        Alerts
                    </Button>
                    <Label as='a' basic color='red' pointing='left'>
                        {this.props.number_alerts}
                    </Label>
            </Button>
          </div>
        );
    }
}


class LoginButtonAndForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            login: '',
            password: '',
	        open: false,
            openRegister: false,
            email: ''
        };
    }

    render() {
	    const {open} = this.state;
        const {openRegister} = this.state;

        return (
            <React.Fragment>
                  <Button
                     content={open ? 'Login' : 'Login'}
                     negative={open}
                     positive={!open}
                     onClick={() => this.setState({open: !this.state.open})}
                  />


            {openRegister ?
                <TransitionablePortal onClose={() => this.setState({openRegister: false})} open={openRegister}>
                      <Segment style={{left: '40%', position: 'fixed', top: '50%', zIndex: 1000}}>
                          <Input focus placeholder='User' onChange={(e) => this.state.login = e.target.value} />
                          <Input focus type='password' placeholder='Password' onChange={(e) => this.state.password = e.target.value} />
                          <Input focus placeholder='Email' onChange={(e) => this.state.email = e.target.value} />
                          <Button onClick={(e) => this.handleRegisterClick(e)}>Register</Button>
                      </Segment>
                  </TransitionablePortal>
                :
                  <TransitionablePortal onClose={() => this.setState({open: false})} open={open}>
                      <Segment style={{left: '40%', position: 'fixed', top: '50%', zIndex: 1000}}>
                          <Input focus placeholder='User' onChange={(e) => this.state.login = e.target.value} />
                          <Input focus type='password' placeholder='Password' onChange={(e) => this.state.password = e.target.value} />
                          <Button onClick={(e) => this.handleLoginClick(e)}>Login</Button>
                          <Button onClick={(e) => this.setState({openRegister: true})}>Register</Button>
                      </Segment>
                  </TransitionablePortal>
            }
            </React.Fragment>

        );
    }

    handleRegisterClick() {
        console.log('Registering');
        console.log(this.state.login);
        console.log(this.state.password);
        console.log(this.state.email);

        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/register",
              data: JSON.stringify({username: this.state.login, password: this.state.password, email: this.state.email}),
              success: function (data) {
                      alert(data);
                    }
        });

        this.setState({openRegister: false, open: false});
    }

    handleLoginClick() {
        console.log(this.state.login);
        console.log(this.state.password);

        // Flask Login
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/login",
              data: JSON.stringify({username: this.state.login, password: this.state.password}),
              success: function (data) {
                      alert(data);
                    }
        });

        // JWT Login
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/auth",
              data: JSON.stringify({username: this.state.login, password: this.state.password}),
              dataType: "json",
              success: function (data) {
                      reduxStore.dispatch({type: 'JWTTOKEN', token: data['access_token']});
                    }
        });
    }
}

class TopMenu extends React.Component {
    state = {activeItem: 'home'}
    handleItemClick = (e, { name }) => {
	    this.setState({ activeItem: name });
	    reduxStore.dispatch({type: 'TOPMENUSELECTION', selection: name});
    }
    constructor(props) {
        super(props);
        reduxStore.dispatch({type: 'TOPMENUSELECTION', selection: 'home'});
    }

    render() {
        const { activeItem } = this.state;

        return (
          <Menu Inverted>
            <Menu.Item name='home' active={activeItem === 'home'} onClick={this.handleItemClick} />
            <Menu.Item name='alerts' active={activeItem === 'alerts'} onClick={this.handleItemClick} />
            <Menu.Menu position='right'>
                <AlertsButton number_alerts={this.props.number_alerts}/>
                <LoginButtonAndForm/>
            </Menu.Menu>

          </Menu>
        );
    }
}


class TopLatestPrices extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let myMenu = []
        if ('POLONIEX' in this.props.latest_prices) {
            for (var key in this.props.latest_prices['POLONIEX']) {
                const price = this.props.latest_prices['POLONIEX'][key];
                myMenu.push(<div key={price}><Menu.Item>{key}: {price}</Menu.Item></div>)
            }
        } else {
            console.warn('Not poloniex');
        }

        return (
            <CSSTransitionGroup
                transitionName="flash"
                transitionEnterTimeout={500}
                transitionLeaveTimeout={300}>

                <Menu Inverted> {myMenu} </Menu>
            </CSSTransitionGroup
        >
        );
    }
}


class CreateAlertPricePercentage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {point: 0, exchange: '', pair: '', below_above: '', time_frame: 0};
    }

    createAlertButtonClicked() {
        if (reduxState.jwt_token == '') {
            console.warn('JWT Token not set for create alert');
            return;
        }

	    $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              headers: {"Authorization": "JWT " + reduxState.jwt_token},
              url: "/createalert",
              data: JSON.stringify({alert: 'pricepercentage', pair: this.state.pair, exchange: this.state.exchange, point: this.state.point, below_above: this.state.below_above, email_notification_value: reduxState.email_notification_value, time_frame: this.state.time_frame}),
              dataType: "json",
              success: (data) => {
                      console.log("Server said this on createalert: ");
                      console.log(data);
                      reduxStore.dispatch({type: 'UPDATEMYALERTS', update: true});
                    }
        });


    }

    render() {
        const timeFrameOptions = [
            { key: 60, text: '1 min', value: 60 },
            { key: 60*5, text: '5 min', value: 60*5 },
            { key: 60*30, text: '30 min', value: 60*30 },
            { key: 60*60, text: '1 hour', value: 60*60 },
            { key: 60*60, text: '4 hour', value: 60*60*4 },
            { key: 60*60, text: '12 hour', value: 60*60*12 },
            { key: 60*60, text: '24 hour', value: 60*60*24 }
        ];

        return(
          <React.Fragment>
              <Input focus placeholder='Price Change Percentage' onChange={(e) => this.setState({point: e.target.value})} />
              <Dropdown placeholder='Pair' fluid multiple selection options={pairOptions} onChange={(e, { value }) => this.setState({pair: value})} />
              <Dropdown placeholder='Exchange' fluid multiple selection options={exchangeOptions} onChange={(e, { value }) => this.setState({exchange: value})} />
              <Dropdown placeholder='Up/Down' fluid selection options={upDownOptions} onChange={(e, { value }) => this.setState({below_above: value})} />
              <Dropdown placeholder='Time Frame' fluid selection options={timeFrameOptions} onChange={(e, { value }) => this.setState({time_frame: value})} />
              <Button onClick={(e) => this.createAlertButtonClicked(e)}>Create Alert</Button>
          </React.Fragment>
        );
    }
}


class CreateAlertPricePoint extends React.Component {
    constructor(props) {
        super(props);
        this.state = {point: 0, exchange: '', pair: '', below_above: ''};
    }

    createAlertButtonClicked() {
        if (reduxState.jwt_token == '') {
            console.warn('JWT Token not set for create alert');
            return;
        }

	    $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              headers: {"Authorization": "JWT " + reduxState.jwt_token},
              url: "/createalert",
              data: JSON.stringify({alert: 'pricepoint', pair: this.state.pair, exchange: this.state.exchange, point: this.state.point, below_above: this.state.below_above, email_notification_value: reduxState.email_notification_value}),
              dataType: "json",
              success: (data) => {
                      console.log("Server said this on createalert: ");
                      console.log(data);
                      reduxStore.dispatch({type: 'UPDATEMYALERTS', update: true});
                    }
        });


    }

    render() {
        const belowAboveOptions = [
          { key: 'above', text: 'Above', value: 'above' },
          { key: 'below', text: 'Below', value: 'below' }
        ];

        return(
          <React.Fragment>
              <Input focus placeholder='Price Point' onChange={(e) => this.setState({point: e.target.value})} />
              <Dropdown placeholder='Pair' fluid multiple selection options={pairOptions} onChange={(e, { value }) => this.setState({pair: value})} />
              <Dropdown placeholder='Exchange' fluid multiple selection options={exchangeOptions} onChange={(e, { value }) => this.setState({exchange: value})} />
              <Dropdown placeholder='Below/Above' fluid selection options={belowAboveOptions} onChange={(e, { value }) => this.setState({below_above: value})} />
              <Button onClick={(e) => this.createAlertButtonClicked(e)}>Create Alert</Button>
          </React.Fragment>
        );
    }
}


class AddNotificationList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {emailValue: ''};
    }

    render() {
        return(
          <React.Fragment>
              <Checkbox label='Email' onChange={(e, data) => reduxStore.dispatch({type: 'SETEMAILNOTIFICATIONVALUE', email_notification_value: data.checked})}/>
          </React.Fragment>
        );
    }
}


class CreateAlert extends React.Component {
    constructor(props) {
        super(props);
        this.state = {activeAlert: 'none'};
    }

    render() {
        return(
             <Segment style={{left: '40%', position: 'fixed', top: '50%', zIndex: 1000}}>
                  <h1>Create Alert</h1>
                  <div>
                    <Button basic onClick={() => this.setState({activeAlert: 'price_point'})}>
                      Price Point
                    </Button>
                    <Button basic color='red' onClick={() => this.setState({activeAlert: 'price_percentage_change'})}>
                      Price Percentage Change
                    </Button>
                    <Button basic color='orange' onClick={() => this.setState({activeAlert: 'price_divergence'})}>
                      Price Divergence
                    </Button>
                    <Button basic color='violet'>
                      Volume Point
                    </Button>
                    <Button basic color='purple'>
                      Volume Percentage Change
                    </Button>
                  </div>


                  {this.state.activeAlert == 'price_point' ? (<CreateAlertPricePoint />) : null}
                  {this.state.activeAlert == 'price_percentage_change' ? (<CreateAlertPricePercentage />) : null}
                  Notifications:
                  <AddNotificationList/>
              </Segment>
        );
    }
}


class Alerts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {createalertopen: false}
    }

    createAlertButtonClicked() {
	    console.log('Create alert button clicked');
    }

    render() {
        let sub_alert_list = [];
        for (var alert_type in this.props.subscribed_alerts) {
            for (let alert of this.props.subscribed_alerts[alert_type]) {
                if (alert_type == "price_point_alert") {
                    sub_alert_list.push(<Segment><List.Item>Alert: Price Point<br/>Exchange: {alert['exchange']}<br/> Market: {alert['pair']}<br/> Point: {alert['point']}<br/> Direction: {alert['direction']}<br/> </List.Item></Segment>);
                } else if (alert_type == "price_percentage_alert") {
                    sub_alert_list.push(<Segment><List.Item>Alert: Price Percentage<br/>Exchange: {alert['exchange']}<br/> Market: {alert['pair']}<br/> Point: {alert['point']}%<br/> Direction: {alert['direction']}<br/> Time Frame: {alert['time_frame']/60}<br/> </List.Item></Segment>);
                } else {
                    console.warn('Unknown alert');
                }
            }
        }

        // TODO(THIS NEEDS TO BE A TABLE JUST LIKE INTERSTING EVENTS)
        console.log('here');
        console.log(this.props.alert_notification);
        let alert_triggered_list = [];
        for (let trigger of this.props.alert_notification) {
            let tdata = trigger['data'];
            console.log(tdata);
            if (tdata['alert_type'] == "pricepoint") {
                alert_triggered_list.push(<Segment><List.Item>Price point triggered for exchange {tdata['trade']['tags']['exchange']} for market {tdata['trade']['tags']['pair']} </List.Item></Segment>);
            } else if (tdata['alert_type'] == "pricepercentage") {
                alert_triggered_list.push(<Segment><List.Item>Price percentage triggered for exchange {tdata['trade']['tags']['exchange']} for market {tdata['trade']['tags']['pair']}.<br/> {tdata['event_description']['message']} </List.Item></Segment>);
            } else {
                console.warn('Unknown alert triggered.')
            }
        }
        console.log(alert_triggered_list);

        return (
            <React.Fragment>
                <Button
                     content={this.state.createalertopen ? 'Create Alert' : 'Create Alert'}
                     negative={this.state.createalertopen}
                     positive={!this.state.createalertopen}
                     onClick={() => this.setState({createalertopen: !this.state.createalertopen})}
                  />

                <TransitionablePortal onClose={() => this.setState({createalertopen: false})} open={this.state.createalertopen}>
                  <CreateAlert />
                </TransitionablePortal>

            <Container>
                <Header as='h2'>Alert Notifications</Header>
                <List>
                    {alert_triggered_list}
                </List>
            </Container>

            <Divider />

            <Container>
                <Header as='h2'>My Alerts</Header>
                <List>
                    {sub_alert_list}
                </List>
            </Container>
            </React.Fragment>
        );
    }
}

class InterestingEvents extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const data = [{
          time: '2:00 Feb 22',
          alert: 'Price spike',
          market: 'BTC_ETH',
          exchange: 'Poloniex',
          message: '5.8% ^'
        }]

        this.props.interesting_events.forEach((event) => {
           data.push({time: event['data']['event_time'], alert: event['data']['event_type'], market: event['data']['market'], exchange: event['data']['exchange'], message: event['data']['message']})
        });

        const columns = [{
            Header: 'Time',
            accessor: 'time' // String-based value accessors!
          }, {
            Header: 'Alert',
            accessor: 'alert'
          }, {
            Header: 'Market',
            accessor: 'market'
          }, {
            Header: 'Exchange',
            accessor: 'exchange'
          }, {
            Header: 'Message',
            accessor: 'message'
          }
        ]

        return <ReactTable
        data={data}
        columns={columns}
        />
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        // this.state.updated_myalerts is to prevent infinite loop of changing redux state.
        // latest_prices is structured as latest_prices[exchange][pair] = 13.21
        this.state = {number_alerts: 0, alert_notification: [], subscribed_alerts: [], logged_in: false, updated_myalerts: true, latest_prices: {}, interesting_events: []}
        // this.state.alert_notification.push(<List.Item>Test Alert Notification</List.Item>);
        // this.state.subscribed_alerts.push(<List.Item>Test My Alert</List.Item>);

        var ws = new WebSocket("ws://46.101.82.15:8080/");
        ws.onmessage = (event) => {
            /*
            {"type": "price_update", "data": {"measurement": "latest_price", "exchange": "POLONIEX", "pair": "BTC_LTC", "price": 0.014792}}
             */

            var data = JSON.parse(event.data);
            console.log(data);
            if (data['type'] == 'price_update') {
                if (!(data['data']['exchange'] in this.state.latest_prices)) {
                    this.state.latest_prices[data['data']['exchange']] = {};
                    console.log('here');
                }
                this.state.latest_prices[data['data']['exchange']][data['data']['pair']] = data['data']['price']
                console.log(this.state.latest_prices)
                this.setState({});
            } else if (data['type'] == 'interesting_event') {
                console.log('Interesting event');
                this.state.interesting_events.push(data);
                this.setState({});
            } else if (data['type'] == 'alert') {
                console.log('ALERT!!!');
                this.state.alert_notification.push(data);
                this.setState({});
            } else if (data['type'] == 'initial_interesting_events') {
                data['data'].forEach((event) => {
                    this.state.interesting_events.push({'data': event});
                });
                console.log(this.state.interesting_events);
                this.setState({});
            } else {
              console.warn('Dont know data type.');
            }

        }

        let reduxChangedState = () => {
            if (reduxState.jwt_token) {
                if (!this.state.logged_in) {  // On first login
                    console.log("First login updating my alerts " + this.state.logged_in);
                    this.updateMyAlerts();
                }

                this.state.logged_in = true;
                if (!this.state.updated_myalerts) {
                    reduxStore.dispatch({type: 'UPDATEMYALERTS', update: false});
                    this.state.updated_myalerts = true;
                    //this.state.updated_myalerts is to prevent infinite loop of changing redux state.
                    setTimeout(() => this.state.updated_myalerts = false, 500);  // Set
                }
            }

            if (reduxState.updateMyAlerts == true) {
                this.updateMyAlerts();
                if (!this.state.updated_myalerts) {
                    reduxStore.dispatch({type: 'UPDATEMYALERTS', update: false});
                    this.state.updated_myalerts = true;
                    //this.state.updated_myalerts is to prevent infinite loop of changing redux state.
                    setTimeout(() => this.state.updated_myalerts = false, 500);
                }
            }

            console.log('Update app state');
            this.setState({}); // Update state for topmenu redux update
        }

        reduxStore.subscribe(reduxChangedState);
    }

    updateMyAlerts() {
        // Update my alerts
        if (!reduxState.jwt_token) {
            console.warn('No JWT token set, cannot update my alerts.');
            return;
        }

        console.log("Updating alerts");

        $.ajax({
              type: "GET",
              headers: {"Authorization": "JWT " + reduxState.jwt_token, contentType: "application/json; charset=utf-8"},
              url: "/getsubscribedalerts",
              dataType: "json",
              success: (data) => {
                      this.state.subscribed_alerts = data;
                      this.setState({});
                    }
        });
    }

    render() {
        const state_ = this.state;
            return (
                <React.Fragment>
                    <TopMenu number_alerts={ this.state.number_alerts} />
                    <TopLatestPrices latest_prices={state_.latest_prices}/>
                    {reduxState.topMenuSelection == 'alerts' ? (
                                <Alerts subscribed_alerts={state_.subscribed_alerts} alert_notification={state_.alert_notification}/>
                        ) : null
                    }
                    {reduxState.topMenuSelection == 'home' ? (
                                <InterestingEvents interesting_events={state_.interesting_events}/>
                        ) : null
                    }
                </React.Fragment>
            );
    }
}

ReactDOM.render(<App/>, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(ButtonExampleLabeledBasic());
//document.body.appendChild(component());
//document.body.appendChild(component());

