(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            ["@nivo/bar" :refer [Bar ResponsiveBar]]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]))

(def histogram-data (atom {}))

(defn fetch-histogram []
  (go
    (let [resp (async/<! (http/get "/simulations/dummy/histograms"))]
      (reset! histogram-data (:body resp)))))

(defonce root (delay (rdc/create-root (js/document.getElementById "app"))))

(defn render-histogram []
  (rdc/render @root
              [:div {:style {:width "100%" :height "500px"}}
               [:>
                ResponsiveBar
                ;; Bar
                {:data [{"country" "AD" "hotdogs" 60 "burgers" 80}
                        {"country" "AE" "hotdogs" 30 "burgers" 50}
                        {"country" "AF" "hotdogs" 70 "burgers" 90}]
                 :keys ["hotdogs" "burgers"]
                 :indexBy "country"
                 :height 500
                 :width 400
                 :margin {:top 50 :right 50 :bottom 50 :left 60}
                 :padding 0.3
                 ;; :colors {:scheme "nivo"}
                 ;; :axisBottom {:tickRotation 0}
                 }]]))

(add-watch histogram-data :redisplay render-histogram)

(defn ^:export ^:dev/after-load init []
  (fetch-histogram))
