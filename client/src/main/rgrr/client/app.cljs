(ns rgrr.client.app
  (:require-macros [cljs.core.async.macros :refer [go]])
  (:require [cljs-http.client :as http]
            [cljs.core.async :as async]
            [reagent.core :as r]
            [reagent.dom.client :as rdc]))

(def histogram-data (atom {}))

(defn fetch-histogram []
  (println "Pre-fetch")
  (go
    (let [resp (async/<! (http/get "/simulations/dummy/histograms"))]
      (prn resp)
      (reset! histogram-data (:body resp))))
  ;; (http/get "/simulations/dummy/histograms"
  ;;           {
  ;;            ;;:handler #(reset! histogram-data (js->clj (.jsonParse (:body %))))
  ;;            :handler (fn [resp] (println "In fetch") (println resp) (reset! histogram-data (:body resp)))
  ;;            :error-handler #(js/console.error "Failed to fetch histogram" %)})
  (println "Post-fetch")
  (println (str @histogram-data)))

(defn histogram-component []
  [:div
   [:h1 "Histogram"]
   [:p (str @histogram-data)]]
  )

(defonce root (delay (rdc/create-root (js/document.getElementById "app"))))

(defn render-histogram []
 (rdc/render @root [histogram-component]))

(add-watch histogram-data :redisplay render-histogram)

(defn ^:export ^:dev/after-load init []
  (fetch-histogram)
  (render-histogram))

(defn simple-component []
  [:div
   [:p "I am a component!"]
   [:p.someclass
    "I have " [:strong "bold"]
    [:span {:style {:color "red"}} " and red "] "text."]])
